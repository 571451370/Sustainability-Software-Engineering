import os

# OS-specific constants
if os.name == 'nt':
    POSIX = False
    DIR_SEPARATOR = "\\"
else:
    POSIX = True
    DIR_SEPARATOR = "/"

SOURCE_METER_DIR_NAME = "SourceMeter-8.2.0-x64-windows"
SOURCE_METER_JAVA_PATH = os.path.join(os.getcwd(), "..", SOURCE_METER_DIR_NAME, "Java", "SourceMeterJava")
SOURCE_METER_PYTHON_PATH = os.path.join(os.getcwd(), "..", SOURCE_METER_DIR_NAME, "Python", "SourceMeterPython")

CLASS_KEEP_COL = ['Name', 'LOC', 'CD', 'CBO', 'NOI']
METHOD_KEEP_COL = ['Name', 'Path', 'LOC', 'NUMPAR', 'CD']

RESULTS_DIR = os.path.join(os.getcwd(), "..", "Results")

JAVA_SAMPLE_PROJ_DIR = os.path.join(os.getcwd(), "..", SOURCE_METER_DIR_NAME, "Java", "Demo", "apache-log4j-1.2.17")
PYTHON_SAMPLE_PROJ_DIR = os.path.join(os.getcwd(), "..", SOURCE_METER_DIR_NAME, "Python", "Demo", "ceilometer")
