--run the alter command in sqlplus.
alter session set NLS_DATE_FORMAT='yyyy/mm/dd:hh:mi:ssam';

spool on-migrateDBS2To3..txt
select sysdate from dual;

INSERT INTO PRIMARY_DS_TYPES ( PRIMARY_DS_TYPE_ID,  PRIMARY_DS_TYPE) SELECT ID, TYPE FROM CMS_DBS_PROD_GLOBAL.PRIMARYDSTYPE;
commit;
select 'Done insert PRIMARY_DS_TYPES' as job from dual;
select sysdate from dual;

INSERT INTO PRIMARY_DATASETS(PRIMARY_DS_ID, PRIMARY_DS_NAME, PRIMARY_DS_TYPE_ID, CREATION_DATE, CREATE_BY)  
SELECT PD.ID, PD.NAME, PD.TYPE, PD.CREATIONDATE, PS.DISTINGUISHEDNAME 
FROM CMS_DBS_PROD_GLOBAL.PRIMARYDATASET PD join CMS_DBS_PROD_GLOBAL.PERSON PS ON  PS.ID=PD.CREATEDBY;
commit;
select 'Done insert PRIMARY_DATASETS' as job from dual;
select sysdate from dual;

INSERT INTO APPLICATION_EXECUTABLES (APP_EXEC_ID, APP_NAME) SELECT ID, EXECUTABLENAME FROM CMS_DBS_PROD_GLOBAL.APPEXECUTABLE;
INSERT INTO RELEASE_VERSIONS ( RELEASE_VERSION_ID, RELEASE_VERSION ) SELECT ID, VERSION FROM CMS_DBS_PROD_GLOBAL.APPVERSION;
INSERT INTO PARAMETER_SET_HASHES ( PARAMETER_SET_HASH_ID, PSET_HASH, PSET_NAME ) SELECT ID, HASH, NAME FROM CMS_DBS_PROD_GLOBAL.QUERYABLEPARAMETERSET;

--FAKING APPLICATIONFAMILY AS OUTPUT_MODULE_LABEL(is it right?), THIS KEEPS THE UNIQUENESS
--GLOBAL_TAG is "UNKNOWN"
--APP_EXEC_ID, RELEASE_VERSION_ID, PARAMETER_SET_HASH_ID, OUTPUT_MODULE_LABEL, GLOBAL_TAG construct the uniqueness of a config.
--Need to update GLOBAL_TAG from DBS2's PROCESSEDDATASET table

INSERT INTO OUTPUT_MODULE_CONFIGS ( OUTPUT_MOD_CONFIG_ID, APP_EXEC_ID, RELEASE_VERSION_ID, PARAMETER_SET_HASH_ID, 
                                    OUTPUT_MODULE_LABEL, GLOBAL_TAG, CREATION_DATE, CREATE_BY) 
SELECT AL.ID, AL.EXECUTABLENAME, AL.APPLICATIONVERSION, AL.PARAMETERSETID, AL.APPLICATIONFAMILY, 'UNKNOWN', AL.CREATIONDATE, PS.DISTINGUISHEDNAME  
FROM CMS_DBS_PROD_GLOBAL.ALGORITHMCONFIG AL JOIN CMS_DBS_PROD_GLOBAL.PERSON PS on PS.ID=AL.CREATEDBY;
commit;
select 'Done insert OUTPUT_MODULE_CONFIGS' as job from dual;
select sysdate from dual;


INSERT INTO PHYSICS_GROUPS ( PHYSICS_GROUP_ID, PHYSICS_GROUP_NAME) SELECT ID, PHYSICSGROUPNAME FROM CMS_DBS_PROD_GLOBAL.PHYSICSGROUP;

--WE WILL USE THE STATUS (FROM DBS-2) TO FILL IN TYPE IN DBS-3, LATER WE CAN FIX THIS
INSERT INTO DATASET_ACCESS_TYPES (DATASET_ACCESS_TYPE_ID, DATASET_ACCESS_TYPE) SELECT ID, STATUS FROM
CMS_DBS_PROD_GLOBAL.PROCDSSTATUS WHERE
STATUS in ('VALID','DELETED', 'INVALID', 'PRODUCTION', 'DEPRECATED');

--ADD a new type "UNKOWN_DBS2_TYPE" with ID=100 to map the VALID and INVALID datasets in DBS2
--INSERT INTO DATASET_ACCESS_TYPES (DATASET_ACCESS_TYPE_ID, DATASET_ACCESS_TYPE) values(100, 'UNKNOWN_DBS2_TYPE');

INSERT INTO DATA_TIERS ( DATA_TIER_ID, DATA_TIER_NAME,CREATION_DATE, CREATE_BY ) SELECT DT.ID, DT.NAME, DT.CREATIONDATE, PS.DISTINGUISHEDNAME
FROM CMS_DBS_PROD_GLOBAL.DATATIER DT join CMS_DBS_PROD_GLOBAL.PERSON PS ON  PS.ID=DT.CREATEDBY
;
INSERT INTO ACQUISITION_ERAS ( ACQUISITION_ERA_NAME, START_DATE ) SELECT DISTINCT AQUISITIONERA, 0 FROM CMS_DBS_PROD_GLOBAL.PROCESSEDDATASET where AQUISITIONERA IS NOT NULL;

INSERT INTO PROCESSED_DATASETS ( PROCESSED_DS_NAME ) SELECT DISTINCT NAME FROM CMS_DBS_PROD_GLOBAL.PROCESSEDDATASET;
commit;
select 'Done insert PROCESSED_DATASETS ' as job from dual;
select sysdate from dual;

--11/1/2011. YG
--Below Comment is not correct anymore. Left it there, just for reference to the old code.
--INSERT ALL DATASETS AS INVALID (IS_DATASET_VALID==0) and DATASET_ACCESS_TYPE="UNKNOWN_DBS2_TYPE" (DATASET_ACCESS_TYPE_ID=100)

INSERT INTO DATASETS (
	 DATASET_ID,                               
	  DATASET,
	   IS_DATASET_VALID,                         
	    PRIMARY_DS_ID,                            
	     PROCESSED_DS_ID,                          
	      DATA_TIER_ID,          
	       DATASET_ACCESS_TYPE_ID,      
	        ACQUISITION_ERA_ID,
		 PHYSICS_GROUP_ID,
		  XTCROSSSECTION,
		    CREATION_DATE,
		     CREATE_BY,
		      LAST_MODIFICATION_DATE,
		       LAST_MODIFIED_BY
	)
SELECT DS.ID, '/' || P.NAME || '/' || DS.NAME || '/' || DT.NAME, 1, P.ID, PDS.PROCESSED_DS_ID, DT.ID, DS.STATUS,
       ACQ.ACQUISITION_ERA_ID, DS.PHYSICSGROUP, DS.XTCROSSSECTION,
       DS.CREATIONDATE, PDCB.DISTINGUISHEDNAME, DS.LASTMODIFICATIONDATE, PDLM.DISTINGUISHEDNAME
       FROM CMS_DBS_PROD_GLOBAL.PROCESSEDDATASET DS
       JOIN CMS_DBS_PROD_GLOBAL.PRIMARYDATASET P
           ON P.ID=DS.PRIMARYDATASET
	   JOIN CMS_DBS_PROD_GLOBAL.DATATIER DT
	       ON DT.ID=DS.DATATIER
	       JOIN PROCESSED_DATASETS PDS
	           ON PDS.PROCESSED_DS_NAME=DS.NAME
		   LEFT OUTER JOIN ACQUISITION_ERAS ACQ
		       ON ACQ.ACQUISITION_ERA_NAME=DS.AQUISITIONERA
		       LEFT OUTER JOIN PHYSICS_GROUPS PG
		           ON DS.PHYSICSGROUP=PG.PHYSICS_GROUP_ID
			   LEFT OUTER JOIN CMS_DBS_PROD_GLOBAL.PERSON PDCB
			       ON DS.CREATEDBY=PDCB.ID
			       LEFT OUTER JOIN CMS_DBS_PROD_GLOBAL.PERSON PDLM
			           ON DS.LASTMODIFIEDBY=PDLM.ID;   

commit;
select 'Done insert DATASET' as job from dual;
select sysdate from dual;

INSERT INTO DATASET_PARENTS(THIS_DATASET_ID, PARENT_DATASET_ID)
SELECT  DSP.THISDATASET, DSP.ITSPARENT FROM CMS_DBS_PROD_GLOBAL.PROCDSPARENT DSP;

commit;
select 'Done inser DATASET_PARENTS' as job from dual;
select sysdate from dual;

--need to rethink YG. Run global_tag update scripts.
INSERT INTO DATASET_OUTPUT_MOD_CONFIGS(DS_OUTPUT_MOD_CONF_ID, DATASET_ID, OUTPUT_MOD_CONFIG_ID)
SELECT PA.ID, PA.DATASET, PA.ALGORITHM FROM CMS_DBS_PROD_GLOBAL.PROCALGO PA;

commit;
select ' Done insert DATASET_OUTPUT_MOD_CONFIGS' as job from dual;
select sysdate from dual;

--How about last modifcation by YG
INSERT INTO BLOCKS
(
  BLOCK_ID,                                 
   BLOCK_NAME,
    DATASET_ID,
     OPEN_FOR_WRITING, 
      BLOCK_SIZE,
       FILE_COUNT,
        CREATION_DATE,
	 CREATE_BY,
	  LAST_MODIFICATION_DATE,
	  LAST_MODIFIED_BY,	
	   ORIGIN_SITE_NAME
	  )
SELECT B.ID, B.NAME, B.DATASET, B.OPENFORWRITING, 
              B.BLOCKSIZE, B.NUMBEROFFILES, B.CREATIONDATE,
	             PDCB.DISTINGUISHEDNAME, B.LASTMODIFICATIONDATE,
		     PDCB2.DISTINGUISHEDNAME, 'UNKNOWN'
		     FROM CMS_DBS_PROD_GLOBAL.BLOCK B
		     LEFT OUTER JOIN CMS_DBS_PROD_GLOBAL.PERSON PDCB
		         ON B.CREATEDBY=PDCB.ID
		     LEFT OUTER JOIN CMS_DBS_PROD_GLOBAL.PERSON PDCB2
                         ON B.LASTMODIFIEDBY=PDCB2.ID;	

commit;
select 'Done insert BLOCKS' as job from dual;
select sysdate from dual;

INSERT into BLOCK_PARENTS(THIS_BLOCK_ID, PARENT_BLOCK_ID)
SELECT BP.THISBLOCK, BP.ITSPARENT FROM CMS_DBS_PROD_GLOBAL.BLOCKPARENT BP; 
commit;
select 'Done insert BLOCKS_PARENTS' as job from dual;
select sysdate from dual;

INSERT INTO FILE_DATA_TYPES ( FILE_TYPE_ID,  FILE_TYPE ) SELECT ID, TYPE FROM CMS_DBS_PROD_GLOBAL.FILETYPE;
commit;
select 'Done insert FILE_DATA_TYPES' as job from dual;
select sysdate from dual;


INSERT INTO FILES
(
  FILE_ID,
   LOGICAL_FILE_NAME,
    IS_FILE_VALID,
     DATASET_ID,
      BLOCK_ID,
       FILE_TYPE_ID,
        CHECK_SUM,
	 EVENT_COUNT,
	  FILE_SIZE,
	   ADLER32,
	    MD5,
	     AUTO_CROSS_SECTION,
	      CREATION_DATE,
	       CREATE_BY,
	        LAST_MODIFICATION_DATE,
		 LAST_MODIFIED_BY
		 )
SELECT F.ID, F.LOGICALFILENAME, 
       (case 
            when F.FILESTATUS = 1 then 1
            when F.FILESTATUS = 2 then 0
            when F.FILESTATUS = 3 then 0
            when F.FILESTATUS = 4 then 0
            when F.FILESTATUS = 5 then 0
            else 0
            end), 
       F.DATASET, F.BLOCK,
       F.FILETYPE, F.CHECKSUM, F.NUMBEROFEVENTS, F.FILESIZE, F.ADLER32,
       F.MD5, F.AUTOCROSSSECTION, F.CREATIONDATE,
       PDCB.DISTINGUISHEDNAME, F.LASTMODIFICATIONDATE, PDLM.DISTINGUISHEDNAME
       FROM CMS_DBS_PROD_GLOBAL.FILES F
       LEFT OUTER JOIN CMS_DBS_PROD_GLOBAL.PERSON PDCB
           ON F.CREATEDBY=PDCB.ID
	   LEFT OUTER JOIN CMS_DBS_PROD_GLOBAL.PERSON PDLM
	       ON F.LASTMODIFIEDBY=PDLM.ID;
commit;
select 'Done insert FILES' as job from dual;
select sysdate from dual;

INSERT INTO FILE_PARENTS(THIS_FILE_ID, PARENT_FILE_ID)
SELECT FP.THISFILE, FP.ITSPARENT FROM CMS_DBS_PROD_GLOBAL.FILEPARENTAGE FP;
commit;
select 'Done insert FILE_PARENTS' as job from dual;
select sysdate from dual;

ALTER TABLE FILE_LUMIS DROP PRIMARY KEY;
ALTER TABLE FILE_LUMIS DROP constraint FL_FLM;
DROP index IDX_FLM_1;
DROP index ID_FLM_2 ;

INSERT /*+ append */ INTO FILE_LUMIS(RUN_NUM, LUMI_SECTION_NUM, FILE_ID)
SELECT R.RUNNUMBER, LS.LUMISECTIONNUMBER, FRL.FILEID FROM CMS_DBS_PROD_GLOBAL.FILERUNLUMI FRL
join CMS_DBS_PROD_GLOBAL.RUNS R on R.ID = FRL.RUN
join CMS_DBS_PROD_GLOBAL.LUMISECTION LS on LS.ID = FRL.LUMI;

commit;
select 'Done insert FILE_LUMIS' as job from dual;
select sysdate from dual;

ALTER TABLE FILE_LUMIS ADD (
  CONSTRAINT FL_FLM
 FOREIGN KEY (FILE_ID)
 REFERENCES FILES (FILE_ID)
    ON DELETE CASCADE);

CREATE INDEX IDX_FLM_1 ON FILE_LUMIS
(FILE_ID);

CREATE INDEX ID_FLM_2 ON FILE_LUMIS (RUN_NUM,FILE_ID);

ALTER TABLE FILE_LUMIS ADD (
  CONSTRAINT PK_FLM
 PRIMARY KEY (RUN_NUM, LUMI_SECTION_NUM, FILE_ID)
 USING INDEX
 );

select 'Done recreate  FILE_LUMIS constraint' as job from dual;
select sysdate from dual;

ALTER TABLE FILE_OUTPUT_MOD_CONFIGS DROP PRIMARY KEY;
ALTER TABLE FILE_OUTPUT_MOD_CONFIGS DROP constraint TUC_FC_1;
ALTER TABLE FILE_OUTPUT_MOD_CONFIGS DROP constraint FL_FC ;
ALTER TABLE FILE_OUTPUT_MOD_CONFIGS DROP constraint OMC_FC;
DROP index IDX_FC_1;
DROP index IDX_FC_2;
INSERT /*+ append */ INTO FILE_OUTPUT_MOD_CONFIGS(FILE_OUTPUT_CONFIG_ID, FILE_ID, OUTPUT_MOD_CONFIG_ID)
SELECT FA.ID, FA.FILEID, FA.ALGORITHM FROM CMS_DBS_PROD_GLOBAL.FILEALGO FA;
commit;
select 'Done insert FILE_OUPTU_MOD_CONFIGS' as job from dual;
select sysdate from dual;
CREATE INDEX IDX_FC_1 ON FILE_OUTPUT_MOD_CONFIGS(FILE_ID);
CREATE INDEX IDX_FC_2 ON FILE_OUTPUT_MOD_CONFIGS(OUTPUT_MOD_CONFIG_ID);
ALTER TABLE FILE_OUTPUT_MOD_CONFIGS ADD (
  CONSTRAINT PK_FC
 PRIMARY KEY
 (FILE_OUTPUT_CONFIG_ID)
    USING INDEX ,
  CONSTRAINT TUC_FC_1
 UNIQUE (FILE_ID, OUTPUT_MOD_CONFIG_ID)
    USING INDEX );

ALTER TABLE FILE_OUTPUT_MOD_CONFIGS ADD (
  CONSTRAINT FL_FC
 FOREIGN KEY (FILE_ID)
 REFERENCES FILES (FILE_ID)
    ON DELETE CASCADE,
  CONSTRAINT OMC_FC
 FOREIGN KEY (OUTPUT_MOD_CONFIG_ID)
 REFERENCES OUTPUT_MODULE_CONFIGS (OUTPUT_MOD_CONFIG_ID)
    ON DELETE CASCADE);

select 'Done recreate  FILE_OUTPUT_MOD_CONFIGS constraint' as job from dual;
select sysdate from dual;

spool off
EXIT;
