import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from io import BytesIO

def parse_healthkit_zip(zip_file):
    """
    Parses an Apple HealthKit export zip file and extracts daily steps and sleep data.

    Args:
        zip_file: BytesIO or path to the exported .zip file from Apple Health.

    Returns:
        steps_df: A DataFrame with columns ['date', 'steps'].
        sleep_df: A DataFrame with columns ['date', 'hours'].
        error: None if succeeded, or an error string if failed.
    """
    try:
        with zipfile.ZipFile(zip_file) as archive:
            with archive.open("apple_health_export/export.xml") as xmlfile:
                tree = ET.parse(xmlfile)
                root = tree.getroot()
                steps = []
                sleep = []
                # Iterate over each record in the XML
                for record in root.iter("Record"):
                    record_type = record.attrib.get("type")
                    start_date = pd.to_datetime(record.attrib.get("startDate"))
                    value = float(record.attrib.get("value", 0))
                    if record_type == "HKQuantityTypeIdentifierStepCount":
                        steps.append({"date": start_date.date(), "steps": value})
                    elif record_type == "HKCategoryTypeIdentifierSleepAnalysis":
                        if int(record.attrib.get("value", 0)) == 1:  # ASLEEP category
                            duration = (
                                pd.to_datetime(record.attrib.get("endDate")) - start_date
                            ).total_seconds() / 3600
                            sleep.append({"date": start_date.date(), "hours": duration})
                steps_df = pd.DataFrame(steps).groupby("date").sum().reset_index()
                sleep_df = pd.DataFrame(sleep).groupby("date").sum().reset_index()
                return steps_df, sleep_df, None
    except Exception as e:
        return None, None, str(e)