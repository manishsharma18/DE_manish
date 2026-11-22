
-- Adapt the stage and file format to the storage location used in your account.
-- Recommended: upload source files to cloud object storage, then create a named stage.
CREATE OR REPLACE FILE FORMAT SKYPOINTS_DB.RAW.JSON_FORMAT TYPE = JSON STRIP_OUTER_ARRAY = FALSE;
CREATE OR REPLACE FILE FORMAT SKYPOINTS_DB.RAW.CSV_FORMAT
    TYPE = CSV FIELD_DELIMITER = '|' SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"' NULL_IF = ('', 'NULL');

-- Example:
-- CREATE OR REPLACE STAGE SKYPOINTS_DB.RAW.SKYPOINTS_STAGE
--   URL='s3://your-bucket/skypoints/' STORAGE_INTEGRATION=YOUR_STORAGE_INTEGRATION;
--
-- JSON landing:
-- COPY INTO SKYPOINTS_DB.RAW.REDEMPTION_RAW (RAW_PAYLOAD, SOURCE_FILE, BATCH_ID)
-- FROM (
--   SELECT $1, METADATA$FILENAME, 'BATCH_20261122'
--   FROM @SKYPOINTS_DB.RAW.SKYPOINTS_STAGE/redemption/
-- )
-- FILE_FORMAT = (FORMAT_NAME = SKYPOINTS_DB.RAW.JSON_FORMAT)
-- ON_ERROR = 'CONTINUE';

-- For standardized Python outputs, use a CSV file format matching the output delimiter
-- and map columns explicitly into a typed staging load. Keep original files immutable.
