
import simpy
import pandas as pd
import numpy as np
from sim_tools.distributions import (Exponential, Lognormal, Uniform)
from scipy.stats import sem, t
import scipy.stats as stats
from vidigi.utils import VidigiPriorityStore, populate_store
import plotly.express as px

class g: # global
    ed_inter_visit = 37.7 
    sdec_inter_visit = 128.8 
    other_inter_visit = 375.7 
    number_of_nelbeds = 434 
    mean_time_in_bed = 13500 
    sd_time_in_bed = 24297
    sim_duration = 86400 
    warm_up_period = (300 * 24 * 60) #convert days into minutes
    number_of_runs = 10
    reneging = 1 #allow reneging behaviour to be switched on or off
    escalation = 1
    escalation_threshold = (40 * 60) #44 hours
    prioritisation = 0
    prop_high_priority = 0.2

class Patient:
    def __init__(self, p_id):
        self.id = p_id
        self.department = ""
        self.priority = 0
        self.inpatient_los = 0
        self.first_request_time = 0
        self.second_request_time = 0

class Model:
    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.event_log = []
        self.patient_counter = 0
        self.run_number = run_number

        # Initialise distributions for generators
        self.ed_inter_visit_dist = Exponential(mean = g.ed_inter_visit, random_seed = (self.run_number+1)*2)
        self.sdec_inter_visit_dist = Exponential(mean = g.sdec_inter_visit, random_seed = (self.run_number+1)*3)
        self.other_inter_visit_dist = Exponential(mean = g.other_inter_visit, random_seed = (self.run_number+1)*4)
        self.exp_time_in_bed_dist = Lognormal((859.0576150300343 * 60), (1852.0617710815982 * 60), random_seed = (self.run_number+1)*5) # governs reneging behaviour - fixed (values 2023-march 2025)
        self.mean_time_in_bed_dist = Lognormal(g.mean_time_in_bed, g.sd_time_in_bed, random_seed = (self.run_number+1)*5) # alterable via the interface
        self.priority_dist = Uniform(0, 1, (self.run_number+1)*6)
        self.init_resources()

    def init_resources(self):
        self.nelbed = VidigiPriorityStore(self.env)
        populate_store(num_resources=g.number_of_nelbeds,
                       simpy_store=self.nelbed,
                       sim_env=self.env)
    
    def generator_ed_arrivals(self): #ed patients
        while True:
            self.patient_counter += 1
            p = Patient(self.patient_counter)
            p.department = "ED"
            self.priority_sample = self.priority_dist.sample()
            p.priority = 0 if (g.prioritisation == 1 and self.priority_sample < g.prop_high_priority) else 1
            p.inpatient_los = self.mean_time_in_bed_dist.sample()
            p.inpatient_exp_los = self.exp_time_in_bed_dist.sample()
            self.env.process(self.attend_ed(p))

            sampled_inter = self.ed_inter_visit_dist.sample() # time to next patient arriving
            yield self.env.timeout(sampled_inter)
    
    def generator_sdec_arrivals(self):
        while True:
            self.patient_counter += 1
            p = Patient(self.patient_counter)
            p.department = "SDEC"
            p.priority = 0 # set all sdec patients as high priority
            p.inpatient_los = self.mean_time_in_bed_dist.sample()
            p.inpatient_exp_los = self.exp_time_in_bed_dist.sample()
            self.env.process(self.attend_other(p))

            sampled_inter = self.sdec_inter_visit_dist.sample()
            yield self.env.timeout(sampled_inter)

    def generator_other_arrivals(self):
        while True:
            self.patient_counter += 1
            p = Patient(self.patient_counter)
            p.department = "Other"
            p.priority = 0 # set all other patients as high priority
            p.inpatient_los = self.mean_time_in_bed_dist.sample()
            p.inpatient_exp_los = self.exp_time_in_bed_dist.sample()
            self.env.process(self.attend_other(p))

            sampled_inter = self.other_inter_visit_dist.sample()
            yield self.env.timeout(sampled_inter)

    def attend_ed(self, patient):
        self.event_log.append(
            {'patient' : patient.id,
             'pathway' : patient.department,
             'event_type' : 'arrival_departure',
             'event' : 'arrival',
             'time' : self.env.now}
        )
        
        self.event_log.append(
            {'patient' : patient.id,
             'pathway' : patient.department,
             'event_type' : 'queue',
             'event' : 'admission_wait_begins',
             'time' : self.env.now}
        )
        patient.first_request_time = self.env.now
        if g.reneging == 0: #if there is no reneging
            if g.escalation == 0: #if there is no escalation
                bed_resource = yield self.nelbed.get(priority=patient.priority)

                self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'resource_use',
                    'event' : 'admission_begins',
                    'time' : self.env.now,
                    'resource_id' : bed_resource.id_attribute
                    }
                    )
            
                sampled_bed_time = patient.inpatient_los
                yield self.env.timeout(sampled_bed_time)

                self.event_log.append(
                {'patient' : patient.id,
                'pathway' : patient.department,
                'event_type' : 'resource_use_end',
                'event' : 'admission_complete',
                'time' : self.env.now,
                'resource_id' : bed_resource.id_attribute
                }
                )

                self.nelbed.put(bed_resource)

                self.event_log.append(
                {'patient' : patient.id,
                'pathway' : patient.department,
                'event_type' : 'arrival_departure',
                'event' : 'depart',
                'time' : self.env.now}
                )
            else: #if there is no reneging but there is escalation
                bed_resource = self.nelbed.get(priority=patient.priority)

                # Wait until one of 2 things happens....
                result_of_queue = (yield bed_resource | # they get a bed
                                    self.env.timeout(g.escalation_threshold)) # they hit the priority threshold
                if bed_resource in result_of_queue: # if they get a bed before being reprioritised
                    self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'resource_use',
                    'event' : 'admission_begins',
                    'time' : self.env.now,
                    'resource_id' : result_of_queue[bed_resource].id_attribute
                    }
                    )
                            
                    sampled_bed_time = patient.inpatient_los
                    yield self.env.timeout(sampled_bed_time)

                    self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'resource_use_end',
                    'event' : 'admission_complete',
                    'time' : self.env.now,
                    'resource_id' : result_of_queue[bed_resource].id_attribute
                    }
                    )

                    self.nelbed.put(result_of_queue[bed_resource])
                else: # if they don't get a bed they are reprioritised
                    bed_resource.cancel() # cancel initial request
                    patient.priority=0 # reprioritise patient
                    bed_resource = yield self.nelbed.get(priority=patient.priority) # make new request and follow normal pathway

                    self.event_log.append(
                        {'patient' : patient.id,
                        'pathway' : patient.department,
                        'event_type' : 'resource_use',
                        'event' : 'admission_begins',
                        'time' : self.env.now,
                        'resource_id' : bed_resource.id_attribute
                        }
                        )
                
                    sampled_bed_time = patient.inpatient_los
                    yield self.env.timeout(sampled_bed_time)

                    self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'resource_use_end',
                    'event' : 'admission_complete',
                    'time' : self.env.now,
                    'resource_id' : bed_resource.id_attribute
                    }
                    )

                    self.nelbed.put(bed_resource)

                self.event_log.append(
                {'patient' : patient.id,
                'pathway' : patient.department,
                'event_type' : 'arrival_departure',
                'event' : 'depart',
                'time' : self.env.now}
                )



        else: # if reneging is turned on
            if g.escalation == 0: # and escalation is not turned on
                bed_resource = self.nelbed.get(priority=patient.priority)

                # Wait until one of 2 things happens....
                result_of_queue = (yield bed_resource | # they get a bed
                                    self.env.timeout(patient.inpatient_exp_los)) # they renege

                if bed_resource in result_of_queue:
                    self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'resource_use',
                    'event' : 'admission_begins',
                    'time' : self.env.now,
                    'resource_id' : result_of_queue[bed_resource].id_attribute
                    }
                    )
                            
                    sampled_bed_time = patient.inpatient_los
                    yield self.env.timeout(sampled_bed_time)

                    self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'resource_use_end',
                    'event' : 'admission_complete',
                    'time' : self.env.now,
                    'resource_id' : result_of_queue[bed_resource].id_attribute
                    }
                    )

                    self.nelbed.put(result_of_queue[bed_resource])
                
                # # If patient reneges
                else:
                    bed_resource.cancel() # SR - Think we need to ensure original request is cancelled at this point
                    self.event_log.append(
                        {'patient' : patient.id,
                        'pathway' : patient.department,
                        'event_type' : 'arrival_departure',
                        'event' : 'renege',
                        'time' : self.env.now,
                        }
                        )
                    
                self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'arrival_departure',
                    'event' : 'depart',
                    'time' : self.env.now}
                    )
            else: # if escalation is turned on and reneging is turned on
                bed_resource = self.nelbed.get(priority=patient.priority)

                # Wait until one of 3 things happens....
                result_of_queue = (yield bed_resource | # they get a bed
                                    self.env.timeout(patient.inpatient_exp_los) |
                                    self.env.timeout(g.escalation_threshold)) # they renege

                if bed_resource in result_of_queue: # they get a bed initially
                    self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'resource_use',
                    'event' : 'admission_begins',
                    'time' : self.env.now,
                    'resource_id' : result_of_queue[bed_resource].id_attribute
                    }
                    )
                            
                    sampled_bed_time = patient.inpatient_los
                    yield self.env.timeout(sampled_bed_time)

                    self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'resource_use_end',
                    'event' : 'admission_complete',
                    'time' : self.env.now,
                    'resource_id' : result_of_queue[bed_resource].id_attribute
                    }
                    )

                    self.nelbed.put(result_of_queue[bed_resource])
                
                # # If patient reneges
                elif patient.inpatient_exp_los < g.escalation_threshold : # they renege
                    bed_resource.cancel() # cancel initial request
                    self.event_log.append(
                        {'patient' : patient.id,
                        'pathway' : patient.department,
                        'event_type' : 'arrival_departure',
                        'event' : 'renege',
                        'time' : self.env.now,
                        }
                        )
                    
                else: # they are reprioritised and wait for a bed
                    bed_resource.cancel() # cancel initial request
                    patient.priority=0 # reprioritise patient
                    patient.second_request_time = self.env.now
                    bed_resource = self.nelbed.get(priority=patient.priority)

                # Wait until one of 2 things happens....
                    result_of_queue = (yield bed_resource | # they get a bed
                                        self.env.timeout(patient.inpatient_exp_los - (patient.second_request_time - patient.first_request_time))) # they renege

                    if bed_resource in result_of_queue:
                        self.event_log.append(
                        {'patient' : patient.id,
                        'pathway' : patient.department,
                        'event_type' : 'resource_use',
                        'event' : 'admission_begins',
                        'time' : self.env.now,
                        'resource_id' : result_of_queue[bed_resource].id_attribute
                        }
                        )
                                
                        sampled_bed_time = patient.inpatient_los
                        yield self.env.timeout(sampled_bed_time)

                        self.event_log.append(
                        {'patient' : patient.id,
                        'pathway' : patient.department,
                        'event_type' : 'resource_use_end',
                        'event' : 'admission_complete',
                        'time' : self.env.now,
                        'resource_id' : result_of_queue[bed_resource].id_attribute
                        }
                        )

                        self.nelbed.put(result_of_queue[bed_resource])
                    
                    # # If patient reneges
                    else:
                        bed_resource.cancel() # SR - Think we need to ensure original request is cancelled at this point
                        self.event_log.append(
                            {'patient' : patient.id,
                            'pathway' : patient.department,
                            'event_type' : 'arrival_departure',
                            'event' : 'renege',
                            'time' : self.env.now,
                            }
                            )
                        
                self.event_log.append(
                    {'patient' : patient.id,
                    'pathway' : patient.department,
                    'event_type' : 'arrival_departure',
                    'event' : 'depart',
                    'time' : self.env.now}
                    )

    
    def attend_other(self, patient):
        self.event_log.append(
            {'patient' : patient.id,
             'pathway' : patient.department,
             'event_type' : 'arrival_departure',
             'event' : 'arrival',
             'time' : self.env.now}
        )

        self.event_log.append(
            {'patient' : patient.id,
             'pathway' : patient.department,
             'event_type' : 'queue',
             'event' : 'admission_wait_begins',
             'time' : self.env.now}
        )

        #self.env.timeout(1)

        bed_resource = yield self.nelbed.get(priority=patient.priority)

        self.event_log.append(
            {'patient' : patient.id,
            'pathway' : patient.department,
            'event_type' : 'resource_use',
            'event' : 'admission_begins',
            'time' : self.env.now,
            'resource_id' : bed_resource.id_attribute
            }
            )
        
        sampled_bed_time = patient.inpatient_los
        yield self.env.timeout(sampled_bed_time)

        self.event_log.append(
        {'patient' : patient.id,
        'pathway' : patient.department,
        'event_type' : 'resource_use_end',
        'event' : 'admission_complete',
        'time' : self.env.now,
        'resource_id' : bed_resource.id_attribute
        }
        )

        self.nelbed.put(bed_resource)

        self.event_log.append(
        {'patient' : patient.id,
        'pathway' : patient.department,
        'event_type' : 'arrival_departure',
        'event' : 'depart',
        'time' : self.env.now}
        )

    def run(self):
        self.env.process(self.generator_ed_arrivals())
        if g.sdec_inter_visit !=0:
            self.env.process(self.generator_sdec_arrivals())
        if g.other_inter_visit !=0:
            self.env.process(self.generator_other_arrivals())
        self.env.run(until=(g.sim_duration + g.warm_up_period))
        self.event_log = pd.DataFrame(self.event_log)
        self.event_log["run"] = self.run_number
        return {'event_log':self.event_log}

class Trial:
    def  __init__(self):
        self.all_event_logs = []
        self.patient_df = pd.DataFrame()
        self.patient_df_nowarmup = pd.DataFrame()
        self.run_summary_df = pd.DataFrame()
        self.trial_summary_df = pd.DataFrame()

    def run_trial(self):
        for run in range(g.number_of_runs):
            my_model = Model(run)
            model_outputs = my_model.run()
            event_log = model_outputs["event_log"]
            
            self.all_event_logs.append(event_log)
        self.all_event_logs = pd.concat(self.all_event_logs)
        self.wrangle_data()
        self.summarise_runs()
        self.summarise_trial()
        return self.all_event_logs, self.patient_df, self.run_summary_df, self.trial_summary_df
    
    def wrangle_data(self):
        df = self.all_event_logs[["patient", "event", "time", "run", "pathway"]]
        df = df.pivot(index=["patient","run", "pathway"], columns="event", values="time")
        df = (df.reset_index()
                .rename_axis(None,axis=1))
        #df["total_los"] = df["depart"] - df["arrival"]
        if "renege" not in df.columns:
            df["renege"] = np.nan
        df["q_time"] = df["admission_begins"] - df["admission_wait_begins"]
        df["q_time_hrs"] = df["q_time"] / 60.0
        df["q_time2_hrs"] = np.where(
                                df["admission_begins"].notnull(),
                                df["admission_begins"] - df["admission_wait_begins"],
                                df["renege"] - df["admission_wait_begins"]
                                ) / 60.0
        df["treatment_time"] = df["admission_complete"] - df["admission_begins"]
        self.patient_df = df
        #self.patient_df_nowarmup = df[df["arrival"] > g.warm_up_period]
        #self.patient_df_nowarmup = df[(df["arrival"] > g.warm_up_period) 
        #                  | (df["admission_begins"] > g.warm_up_period)
        #                  | (df["renege"] > g.warm_up_period)]
        # columns_to_check = [
        # 'admission_begins', 'admission_complete', 'admission_wait_begins',
        # 'arrival', 'depart', 'treatment_time', 'renege'
        # ]
        # self.patient_df_nowarmup = df[df[columns_to_check].gt(g.warm_up_period).any(axis=1)]

    def summarise_runs(self):
        run_summary = self.patient_df
        # note that q_time is na where a patient is not admitted so is automatically omitted from summary calcs
        run_summary = run_summary.groupby("run").agg(
            total_demand=("arrival", lambda x: (x > g.warm_up_period).sum()),
            discharges=("patient", lambda x: (
                        ((run_summary.loc[x.index, "admission_complete"] > g.warm_up_period))
                        .sum())),
            
            #("admission_complete", lambda x: (x > g.warm_up_period).sum()),
            ed_demand=("patient", lambda x: (
                        ((run_summary.loc[x.index, "arrival"] > g.warm_up_period
                        ) & (run_summary.loc[x.index, "pathway"] == "ED")).sum())),
            ed_admissions=("patient", lambda x: (
                        ((run_summary.loc[x.index, "admission_begins"] > g.warm_up_period
                        ) & (run_summary.loc[x.index, "pathway"] == "ED")).sum())),
            reneged=("renege", lambda x: (x > g.warm_up_period).sum() / (g.sim_duration/1440)),
            ed_mean_qtime=("q_time", lambda x: (
                        x[
                            (run_summary.loc[x.index, "admission_begins"] > g.warm_up_period) &
                            (run_summary.loc[x.index, "pathway"] == "ED") &
                            x.notna()
                        ].mean() / 60.0
            )),
            ed_sd_qtime=("q_time", lambda x: (
                        x[
                            (run_summary.loc[x.index, "admission_begins"] > g.warm_up_period) &
                            (run_summary.loc[x.index, "pathway"] == "ED") &
                            x.notna()
                        ].std() / 60.0
            )),
            ed_min_qtime=("q_time", lambda x: (
                        x[
                            (run_summary.loc[x.index, "admission_begins"] > g.warm_up_period) &
                            (run_summary.loc[x.index, "pathway"] == "ED") &
                            x.notna()
                        ].min() / 60.0
            )),
            ed_max_qtime=("q_time", lambda x: (
                        x[
                            (run_summary.loc[x.index, "admission_begins"] > g.warm_up_period) &
                            (run_summary.loc[x.index, "pathway"] == "ED") &
                            x.notna()
                        ].max() / 60.0
            )),
            ed_95=("q_time", lambda x: (
                np.percentile(
                    x[
                        (run_summary.loc[x.index, "admission_begins"] > g.warm_up_period) &
                        (run_summary.loc[x.index, "pathway"] == "ED") &
                        x.notna()
                    ],
                    95
                ) / 60.0
            )),
            dtas_12hr=("q_time", lambda x: (
                        x[
                            (run_summary.loc[x.index, "admission_begins"] > g.warm_up_period) &
                            (run_summary.loc[x.index, "pathway"] == "ED") &
                            x.notna()
                        ].gt(12 * 60).sum() / (g.sim_duration/1440)
            )),
            los_12hr=("q_time2_hrs", lambda x: (
                        x[  (
                            (run_summary.loc[x.index, "admission_begins"] > g.warm_up_period) |
                            (run_summary.loc[x.index, "renege"] > g.warm_up_period)
                            ) &
                            (run_summary.loc[x.index, "pathway"] == "ED") &
                            x.notna()
                        ].gt(12).sum() / (g.sim_duration/1440)
            )),
            sdec_admissions=("patient", lambda x: (
                        ((run_summary.loc[x.index, "admission_begins"] > g.warm_up_period
                        ) & (run_summary.loc[x.index, "pathway"] == "SDEC")).sum()))
        )
        run_summary=run_summary.drop(columns=["ed_demand", "ed_sd_qtime"])
        run_summary=run_summary.rename(columns={
            'total_demand':'Total Admission Demand',
            'discharges':'Total Discharges',
            'ed_admissions': 'Admissions via ED',
            'reneged': 'Reneged (per day)',
            'ed_mean_qtime':'Mean Q Time (Hrs)',
            'ed_min_qtime':'Min Q Time (Hrs)',
            'ed_max_qtime':'Max Q Time (Hrs)',
            'ed_95':'95th Percentile Q Time (Hrs)',
            'dtas_12hr':'12hr DTAs (per day)',
            'los_12hr':'12hr LoS Breaches (per day)',
            'sdec_admissions':'SDEC Admissions'
        })
        self.run_summary_df = run_summary

    def summarise_trial(self):
        trial_summary = self.run_summary_df
        trial_summary = trial_summary.transpose()
        newdf = pd.DataFrame(index=trial_summary.index)
        newdf.index.name = "Metric"
        newdf["Mean"] = trial_summary.mean(axis=1)
        newdf["St. dev"] = trial_summary.std(axis=1)
        newdf['St. error'] = sem(trial_summary, axis=1, nan_policy='omit')
        # Confidence intervals (95%) - t distribution method accounts for sample size
        confidence = 0.95
        h = newdf['St. error'] * t.ppf((1 + confidence) / 2, g.number_of_runs - 1)
        newdf['Lower 95% CI'] = newdf['Mean'] - h
        newdf['Upper 95% CI'] = newdf['Mean'] + h
        newdf['Min'] = trial_summary.min(axis=1)
        newdf['Max'] = trial_summary.max(axis=1)
        newdf=newdf.round(2)
        self.trial_summary_df = newdf
    

#For testing
# my_trial = Trial()
# print(f"Running {g.number_of_runs} simulations......")
# all_event_logs, patient_df, run_summary_df, trial_summary_df =  my_trial.run_trial()
# # # # # #display(my_trial.all_event_logs.head(1000))
# display(my_trial.patient_df.tail(1000))
# # # # # #display(my_trial.patient_df_nowarmup.head(1000))
# # # # # display(my_trial.run_summary_df)
# # # # # display(my_trial.trial_summary_df)

# # # # # test for no admission complete and no renege without depart timestamps
# # # display(patient_df[(~patient_df['admission_complete'].isna()) & (patient_df['depart'].isna())])
# # # display(patient_df[(~patient_df['admission_complete'].isna()) & (patient_df['depart'].isna())])
        
# # #####Number of beds occupied

# minutes = pd.Series(range(g.sim_duration - 1440, g.sim_duration))

# run0_df = patient_df[patient_df['run'] == 0]
# beds = ((run0_df["admission_begins"].values[:, None] < minutes.values) &
#         ((run0_df["admission_complete"].values[:, None] > minutes.values) |
#          run0_df["admission_complete"].isna().values[:, None])).sum(axis=0)

# beds_df = pd.DataFrame({"minutes": minutes, "beds": beds})

# fig = px.line(beds_df, x = "minutes", y = "beds")

# fig.add_hline(y=434, line_dash="dash", line_color="lightblue",
#               opacity=0.5, 
#               annotation_text="max. beds", 
#               annotation_position="top left")

# fig.update_layout(template="plotly_dark")

# fig.show()