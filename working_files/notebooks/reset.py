import dataset
import datetime as dt
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine

sqlalchemy_uri = 'postgresql://datascientist:1234thumbwar@thor.rtp.rti.org:5432/cfs'
#sqlalchemy_uri = 'postgresql://datascientist:@localhost:5432/cfs'

db = dataset.connect(sqlalchemy_uri)
engine = create_engine(sqlalchemy_uri)

def reset_db():
    """
    Remove and recreate tables to prepare for reloading the db
    """
    db.query("DROP TABLE IF EXISTS note CASCADE;")
    db.query("DROP TABLE IF EXISTS note_author CASCADE;")
    db.query("DROP TABLE IF EXISTS call CASCADE;")
    db.query("DROP TABLE IF EXISTS call_source CASCADE;")
    db.query("DROP TABLE IF EXISTS call_unit CASCADE;")
    db.query("DROP TABLE IF EXISTS city CASCADE;")
    db.query("DROP TABLE IF EXISTS officer_name CASCADE;")
    db.query("DROP TABLE IF EXISTS shift CASCADE;")
    db.query("DROP TABLE IF EXISTS call_log CASCADE;")
    db.query("DROP TABLE IF EXISTS transaction CASCADE;")
    db.query("DROP TABLE IF EXISTS close_code CASCADE;")
    db.query("DROP TABLE IF EXISTS ucr_descr CASCADE;")
    db.query("DROP TABLE IF EXISTS incident CASCADE;")
    db.query("DROP TABLE IF EXISTS modus_operandi CASCADE;")
    db.query("DROP TABLE IF EXISTS mo_item CASCADE;")
    db.query("DROP TABLE IF EXISTS bureau CASCADE;")
    db.query("DROP TABLE IF EXISTS case_status CASCADE;")
    db.query("DROP TABLE IF EXISTS division CASCADE;")
    db.query("DROP TABLE IF EXISTS unit CASCADE;")
    db.query("DROP TABLE IF EXISTS investigation_status CASCADE;")
    db.query("DROP TABLE IF EXISTS weapon CASCADE;")
    db.query("DROP TABLE IF EXISTS weapon_group CASCADE;")
    db.query("DROP TABLE IF EXISTS premise CASCADE;")
    db.query("DROP TABLE IF EXISTS premise_group CASCADE;")
    db.query("DROP TABLE IF EXISTS nature CASCADE;")
    db.query("DROP TABLE IF EXISTS oos_code CASCADE;")
    db.query("DROP TABLE IF EXISTS out_of_service CASCADE;")

    
    db.query("""
    CREATE TABLE ucr_descr
    (
      ucr_descr_id serial NOT NULL,
      short_descr text,
      long_descr text,
      CONSTRAINT ucr_descr_pk PRIMARY KEY (ucr_descr_id)
    );
    """)
    
    db.query("""
    CREATE TABLE bureau
    (
      bureau_id serial NOT NULL,
      descr text,
      CONSTRAINT bureau_pk PRIMARY KEY (bureau_id)
    );
    """)
    
    db.query("""
    CREATE TABLE division
    (
      division_id serial NOT NULL,
      descr text,
      CONSTRAINT division_pk PRIMARY KEY (division_id)
    );
    """)
    
    db.query("""
    CREATE TABLE investigation_status
    (
      investigation_status_id serial NOT NULL,
      descr text,
      CONSTRAINT investigation_status_pk PRIMARY KEY (investigation_status_id)
    );
    """)
    
    db.query("""
    CREATE TABLE case_status
    (
      case_status_id serial NOT NULL,
      descr text,
      CONSTRAINT case_status_pk PRIMARY KEY (case_status_id)
    );
    """)
    
    db.query("""
    CREATE TABLE unit
    (
      unit_id serial NOT NULL,
      descr text,
      CONSTRAINT unit_pk PRIMARY KEY (unit_id)
    );
    """)
    
    db.query("""
    CREATE TABLE weapon_group
    (
      weapon_group_id serial NOT NULL,
      descr text,
      CONSTRAINT weapon_group_pk PRIMARY KEY (weapon_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE premise_group
    (
      premise_group_id serial NOT NULL,
      descr text,
      CONSTRAINT premise_group_pk PRIMARY KEY (premise_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE weapon
    (
      weapon_id serial NOT NULL,
      descr text,
      weapon_group_id int,
      CONSTRAINT weapon_pk PRIMARY KEY (weapon_id),
      CONSTRAINT weapon_group_weapon_fk FOREIGN KEY (weapon_group_id) REFERENCES weapon_group (weapon_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE premise
    (
      premise_id serial NOT NULL,
      descr text,
      premise_group_id int,
      CONSTRAINT premise_pk PRIMARY KEY (premise_id),
      CONSTRAINT premise_group_premise_fk FOREIGN KEY (premise_group_id) REFERENCES premise_group (premise_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE city
    (
      city_id serial NOT NULL,
      descr text,
      CONSTRAINT city_pk PRIMARY KEY (city_id)
    );
    """)
    
    db.query("""
    CREATE TABLE incident
    (
      incident_id bigint NOT NULL,
      case_id bigint UNIQUE,
      time_filed timestamp without time zone,
      month_filed int,
      week_filed int,
      dow_filed int,
      street_num int,
      street_name text,
      city_id int,
      zip int,
      geox double precision,
      geoy double precision,
      beat text,
      district text,
      sector text,
      premise_id int,
      weapon_id int,
      domestic boolean,
      juvenile boolean,
      gang_related boolean,
      emp_bureau_id int,
      emp_division_id int,
      emp_unit_id int,
      num_officers int,
      investigation_status_id int,
      investigator_unit_id int,
      case_status_id int,
      ucr_code int,
      ucr_descr_id int,
      committed boolean,
      
      CONSTRAINT incident_pk PRIMARY KEY (incident_id),
      
      CONSTRAINT case_status_incident_fk
        FOREIGN KEY (case_status_id) REFERENCES case_status (case_status_id),
      CONSTRAINT bureau_incident_fk
        FOREIGN KEY (emp_bureau_id) REFERENCES bureau (bureau_id),
      CONSTRAINT division_incident_fk
        FOREIGN KEY (emp_division_id) REFERENCES division (division_id),
      CONSTRAINT unit_incident_emp_fk
        FOREIGN KEY (emp_unit_id) REFERENCES unit (unit_id),
      CONSTRAINT unit_incident_investigator_fk
        FOREIGN KEY (investigator_unit_id) REFERENCES unit (unit_id),
      CONSTRAINT investigation_status_incident_fk
        FOREIGN KEY (investigation_status_id) REFERENCES investigation_status (investigation_status_id),
      CONSTRAINT premise_incident_fk
        FOREIGN KEY (premise_id) REFERENCES premise (premise_id),
      CONSTRAINT weapon_incident_fk
        FOREIGN KEY (weapon_id) REFERENCES weapon (weapon_id),
      CONSTRAINT city_incident_fk
        FOREIGN KEY (city_id) REFERENCES city (city_id),
      CONSTRAINT ucr_descr_incident_fk
        FOREIGN KEY (ucr_descr_id) REFERENCES ucr_descr (ucr_descr_id)
    );
    """)
    
    db.query("""
    CREATE TABLE mo_item
    (
      mo_item_id serial NOT NULL,
      item_descr text,
      mo_group_id serial NOT NULL,
      group_descr text,
      CONSTRAINT mo_item_pk PRIMARY KEY (mo_item_id, mo_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE modus_operandi
    (
      incident_id bigint,
      mo_id bigint,
      mo_group_id int,
      mo_item_id int,
      
      CONSTRAINT mo_pk PRIMARY KEY (mo_id),
      
      CONSTRAINT incident_modus_operandi_fk FOREIGN KEY (incident_id) REFERENCES incident (incident_id),
      CONSTRAINT mo_item_modus_operandi_fk FOREIGN KEY (mo_item_id, mo_group_id) 
        REFERENCES mo_item (mo_item_id, mo_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE call_source
    (
      call_source_id serial NOT NULL,
      descr text,
      CONSTRAINT call_source_pk PRIMARY KEY (call_source_id)
    );
    """)
    
    db.query("""
    CREATE TABLE call_unit
    (
      call_unit_id serial NOT NULL,
      descr text,
      CONSTRAINT call_unit_pk PRIMARY KEY (call_unit_id)
    );
    """)
    
    db.query("""
    CREATE TABLE close_code
    (
      close_code_id serial NOT NULL,
      descr text,
      CONSTRAINT close_code_pk PRIMARY KEY (close_code_id)
    );
    """)
    
    db.query("""
    CREATE TABLE nature
    (
      nature_id serial NOT NULL,
      descr text,
      CONSTRAINT nature_pk PRIMARY KEY (nature_id)
    );
    """)
    
    db.query("""
    CREATE TABLE call
    (
      call_id bigint NOT NULL,
      month_received int,
      week_received int,
      dow_received int,
      hour_received int,
      case_id bigint,
      call_source_id int,
      primary_unit_id int,
      first_dispatched_id int,
      reporting_unit_id int,
      street_num int,
      street_name text,
      city_id int,
      zip int,
      crossroad1 text,
      crossroad2 text,
      geox double precision,
      geoy double precision,
      beat text,
      district text,
      sector text,
      business text,
      nature_id int,
      priority text,
      report_only boolean,
      cancelled boolean,
      time_received timestamp without time zone,
      time_routed timestamp without time zone,
      time_finished timestamp without time zone,
      first_unit_dispatch timestamp without time zone,
      first_unit_enroute timestamp without time zone,
      first_unit_arrive timestamp without time zone,
      first_unit_transport timestamp without time zone,
      last_unit_clear timestamp without time zone,
      time_closed timestamp without time zone,
      close_code_id int,
      close_comments text,
      
      CONSTRAINT call_pk PRIMARY KEY (call_id),
      
      CONSTRAINT call_source_call_fk
        FOREIGN KEY (call_source_id) REFERENCES call_source (call_source_id),
      CONSTRAINT call_unit_call_primary_unit_fk
        FOREIGN KEY (primary_unit_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT call_unit_call_first_dispatched_fk
        FOREIGN KEY (first_dispatched_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT call_unit_call_reporting_unit_fk
        FOREIGN KEY (reporting_unit_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT city_call_fk
        FOREIGN KEY (city_id) REFERENCES city (city_id),
      CONSTRAINT close_code_call_fk
        FOREIGN KEY (close_code_id) REFERENCES close_code (close_code_id),
      --There is some mismatch here that might be valid; no constraint for now
      --CONSTRAINT incident_call_fk
      --  FOREIGN KEY (case_id) REFERENCES incident (case_id),
      CONSTRAINT nature_call_fk
        FOREIGN KEY (nature_id) REFERENCES nature (nature_id)
    );
    """)
    
    db.query("""
    CREATE TABLE note_author
    (
      note_author_id serial NOT NULL,
      descr text,
      CONSTRAINT note_author_pk PRIMARY KEY (note_author_id)
    );
    """)
    
    db.query("""
    CREATE TABLE note
    (
      note_id serial NOT NULL,
      body text,
      time_recorded timestamp without time zone,
      note_author_id int,
      call_id bigint,
      CONSTRAINT note_pk PRIMARY KEY (note_id),
      
      CONSTRAINT call_note_fk FOREIGN KEY (call_id) REFERENCES call (call_id),
      CONSTRAINT note_author_note_fk FOREIGN KEY (note_author_id) REFERENCES note_author (note_author_id)
    );
    """)
    
    db.query("""
    CREATE TABLE officer_name
    (
        officer_name_id serial NOT NULL,
        officer_id bigint,
        name text,
        
        CONSTRAINT officer_name_pk PRIMARY KEY (officer_name_id)
    );
    """)
    
    db.query("""
    CREATE TABLE shift
    (
        shift_id bigint NOT NULL,
        shift_unit_id bigint,
        call_unit_id int,
        officer_id int,
        time_in timestamp without time zone,
        time_out timestamp without time zone,
        unit text,
        division text,
        section text,
        
        CONSTRAINT shift_pk PRIMARY KEY (shift_id),
        -- shift_unit_id is referenced by call_log and out_of_service, but it's not unique, so it can't
        -- be the primary key
        CONSTRAINT call_unit_shift_fk FOREIGN KEY (call_unit_id) REFERENCES call_unit (call_unit_id)
        -- officer_id references officer_name, but it isn't unique in that table, so no FK constraint
    );
    """)

    db.query("""
    CREATE TABLE transaction
    (
      transaction_id serial NOT NULL,
      descr text,
      CONSTRAINT transaction_pk PRIMARY KEY (transaction_id)
    )
    """)
    
    db.query("""
    CREATE TABLE call_log
    (
      call_log_id bigint NOT NULL,
      transaction_id int,
      shift_unit_id int,
      time_recorded timestamp without time zone,
      call_id bigint,
      call_unit_id int,
      close_code_id int,
      
      CONSTRAINT call_log_pk PRIMARY KEY (call_log_id),
      
      -- shift_unit_id references shift.shift_unit_id, but the latter isn't unique, so no FK constraint
      CONSTRAINT call_unit_call_log_fk FOREIGN KEY (call_unit_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT call_call_log_fk FOREIGN KEY (call_id) REFERENCES call (call_id),
      CONSTRAINT close_code_call_log_fk FOREIGN KEY (close_code_id) REFERENCES close_code (close_code_id),
      CONSTRAINT transaction_call_log_fk FOREIGN KEY (transaction_id) REFERENCES transaction (transaction_id)
    );
    """)
    
    db.query("""
    CREATE TABLE oos_code
    (
      oos_code_id serial NOT NULL,
      descr text,
      
      CONSTRAINT oos_code_pk PRIMARY KEY (oos_code_id)
    );
    """)
    
    db.query("""
    CREATE TABLE out_of_service
    (
      oos_id bigint NOT NULL,
      call_unit_id int,
      shift_unit_id int,
      oos_code_id int,
      location text,
      comments text,
      start_time timestamp without time zone,
      end_time timestamp without time zone,
      duration interval,
      
      CONSTRAINT oos_pk PRIMARY KEY (oos_id),
      
      -- shift_unit_id references shift.shift_unit_id, but the latter isn't unique, so no FK constraint
      CONSTRAINT call_unit_oos_fk FOREIGN KEY (call_unit_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT oos_code_oos_fk FOREIGN KEY (oos_code_id) REFERENCES oos_code (oos_code_id)
    );
    """)
      
    
reset_db()
