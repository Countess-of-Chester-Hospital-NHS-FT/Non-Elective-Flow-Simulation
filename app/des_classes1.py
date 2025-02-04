
import simpy
import pandas as pd
from sim_tools.distributions import (Exponential, Lognormal, Uniform)
from scipy.stats import sem, t
import scipy.stats as stats
from vidigi.utils import VidigiPriorityStore, populate_store

class g: # global
    ed_inter_visit = 37.7 
    sdec_inter_visit = 128.8 
    other_inter_visit = 375.7 
    number_of_nelbeds = 434 
    mean_time_in_bed = 13500 
    sd_time_in_bed = 24297
    sim_duration = 86400 
    warm_up_period = 86400 
    number_of_runs = 10

class Patient:
    def __init__(self, p_id):
        self.id = p_id
        self.department = ""
        self.renege_time = 0
        self.priority = 0
        self.priority_update = 0
        self.sdec_other_priority = 0.8

class Model:
    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.event_log = []
        self.patient_counter = 0
        self.run_number = run_number

        # Initialise distributions for generators
        self.ed_inter_visit_dist = Exponential(mean = g.ed_inter_visit, random_seed = self.run_number*2)
        self.sdec_inter_visit_dist = Exponential(mean = g.sdec_inter_visit, random_seed = self.run_number*3)
        self.other_inter_visit_dist = Exponential(mean = g.other_inter_visit, random_seed = self.run_number*4)
        self.mean_time_in_bed_dist = Lognormal(g.mean_time_in_bed, g.sd_time_in_bed, random_seed = self.run_number*5)
        self.renege_time = Uniform(0, 9000, random_seed = self.run_number*6)
        self.priority_update = Uniform(0, 9000, random_seed = self.run_number*7)
        self.priority = Uniform(1,2, random_seed = self.run_number*8)
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
            p.renege_time = self.renege_time.sample()
            p.priority = round(self.priority.sample())
            p.priority_update = self.priority_update.sample()
            self.env.process(self.attend_ed(p))

            sampled_inter = self.ed_inter_visit_dist.sample() # time to next patient arriving
            yield self.env.timeout(sampled_inter)
    
    def generator_sdec_arrivals(self):
        while True:
            self.patient_counter += 1
            p = Patient(self.patient_counter)
            p.department = "SDEC"
            p.priority = 0.8 # set all sdec patients as high priority
            self.env.process(self.attend_other(p))

            sampled_inter = self.sdec_inter_visit_dist.sample()
            yield self.env.timeout(sampled_inter)

    def generator_other_arrivals(self):
        while True:
            self.patient_counter += 1
            p = Patient(self.patient_counter)
            p.department = "Other"
            p.priority = 0.8 # set all other patients as high priority
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

        bed_resource = self.nelbed.get(priority=patient.priority)

        # Wait until one of 3 things happens....
        result_of_queue = (yield bed_resource | # they get a bed
                            self.env.timeout(patient.renege_time)| # they renege
                            self.env.timeout(patient.priority_update)) # they become higher priority

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
                    
            sampled_bed_time = self.mean_time_in_bed_dist.sample()
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
            
        # If the result of the queue was increase of priority
        elif patient.priority_update < patient.renege_time:
            bed_resource.cancel() # SR - Think we need to ensure original request is cancelled at this point
            patient.priority = patient.priority - 2.2 #arbitrary priority increase
            self.event_log.append(
            {'patient' : patient.id,
            'pathway' : patient.department,
            'event_type' : 'other',
            'event' : 'priority_increase',
            'time' : self.env.now,
            }
            )
        #     # Make another bed request with new priority
            bed_resource_new = yield self.nelbed.get(priority=patient.priority)
            self.event_log.append(
            {'patient' : patient.id,
            'pathway' : patient.department,
            'event_type' : 'resource_use',
            'event' : 'admission_begins',
            'time' : self.env.now,
            'resource_id' : bed_resource_new.id_attribute
            }
            )
            
            sampled_bed_time = self.mean_time_in_bed_dist.sample()
            yield self.env.timeout(sampled_bed_time)

            self.nelbed.put(bed_resource_new)

            self.event_log.append(
            {'patient' : patient.id,
            'pathway' : patient.department,
            'event_type' : 'resource_use_end',
            'event' : 'admission_complete',
            'time' : self.env.now,
            'resource_id' : bed_resource_new.id_attribute
            }
            )
        
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
        
        sampled_bed_time = self.mean_time_in_bed_dist.sample()
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
        self.env.process(self.generator_sdec_arrivals())
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
        return self.all_event_logs, self.patient_df, self.patient_df_nowarmup, self.run_summary_df, self.trial_summary_df
    
    def wrangle_data(self):
        df = self.all_event_logs[["patient", "event", "time", "run", "pathway"]]
        df = df.pivot(index=["patient","run", "pathway"], columns="event", values="time")
        df = (df.reset_index()
                .rename_axis(None,axis=1))
        #df["total_los"] = df["depart"] - df["arrival"]
        df["q_time"] = df["admission_begins"] - df["admission_wait_begins"]
        df["q_time_hrs"] = df["q_time"] / 60.0
        df["treatment_time"] = df["admission_complete"] - df["admission_begins"]
        self.patient_df = df
        self.patient_df_nowarmup = df[df["arrival"] > g.warm_up_period]

    def summarise_runs(self):
        run_summary = self.patient_df_nowarmup
        # note that q_time is na where a patient is not admitted so is automatically omitted from summary calcs
        run_summary = run_summary.groupby("run").agg(
            total_demand=("patient", "count"),
            ed_demand=("patient", lambda x: x[self.patient_df_nowarmup["pathway"] == "ED"].count()),
            ed_admissions=("patient", lambda x: x[(self.patient_df_nowarmup["pathway"] == "ED") & (~pd.isna(self.patient_df_nowarmup["admission_begins"]))].count()),
            reneged=("renege", lambda x: x.notna().sum()),
            ed_mean_qtime=("q_time",
                            lambda x: x[self.patient_df_nowarmup["pathway"] == "ED"].mean() / 60.0),
            ed_sd_qtime=("q_time",
                            lambda x: x[self.patient_df_nowarmup["pathway"] == "ED"].std() / 60.0),
            ed_min_qtime=("q_time",
                            lambda x: x[self.patient_df_nowarmup["pathway"] == "ED"].min() / 60.0),
            ed_max_qtime=("q_time",
                            lambda x: x[self.patient_df_nowarmup["pathway"] == "ED"].max() / 60.0),
            ed_95=("q_time",
                            lambda x: x[self.patient_df_nowarmup["pathway"] == "ED"].quantile(0.95) / 60.0),
            dtas_12hr=("q_time", lambda x: x[self.patient_df_nowarmup["pathway"] == "ED"].gt(12 * 60).sum() / (g.sim_duration/1440)),
            under_4hr=("q_time", lambda x: x[self.patient_df_nowarmup["pathway"] == "ED"].lt(4 * 60).sum()),
            sdec_admissions=("pathway", lambda x: x[(self.patient_df_nowarmup["pathway"] == "SDEC") & (~pd.isna(self.patient_df_nowarmup["admission_begins"]))].count())
        )
        run_summary["admitted_perf_4hr"]=(run_summary["under_4hr"] / run_summary["ed_admissions"])*100 #
        run_summary["total_perf_4hr"]=(run_summary["under_4hr"] / run_summary["ed_demand"])*100
        run_summary=run_summary.drop(columns=["ed_demand", "under_4hr", "ed_sd_qtime"])
        run_summary=run_summary.rename(columns={
            'total_demand':'Total Demand',
            'ed_admissions': 'ED Admissions',
            'reneged': 'Reneged',
            'ed_mean_qtime':'Mean Q Time (Hrs)',
            'ed_min_qtime':'Min Q Time (Hrs)',
            'ed_max_qtime':'Max Q Time (Hrs)',
            'ed_95':'95th Percentile Q Time (Hrs)',
            'dtas_12hr':'12hr DTAs (per day)',
            'sdec_admissions':'SDEC Admissions',
            'admitted_perf_4hr':'Admitted 4hr DTA Performance (%)',
            'total_perf_4hr':'Overall 4hr DTA Performance (%)'
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
my_trial = Trial()
print(f"Running {g.number_of_runs} simulations......")
all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df =  my_trial.run_trial()
display(my_trial.all_event_logs.head(1000))
display(my_trial.patient_df.head(1000))
# display(my_trial.patient_df_nowarmup.head(1000))
# display(my_trial.run_summary_df)
# display(my_trial.trial_summary_df)