import xml.etree.ElementTree as ET
import zipfile
import pandas as pd

def parse_healthkit_zip(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as z:
        if "export.xml" not in z.namelist():
            return None, "'export.xml' not found in the ZIP file."
        with z.open("export.xml") as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            steps = []
            sleep = []
            for record in root.findall("Record"):
                rtype = record.get("type")
                start = record.get("startDate")
                end = record.get("endDate")
                value = record.get("value")
                if rtype == "HKQuantityTypeIdentifierStepCount":
                    steps.append({"date": start[:10], "steps": int(float(value))})
                elif rtype == "HKCategoryTypeIdentifierSleepAnalysis":
                    sleep.append({"start": start, "end": end, "type": value})
            return {
                "steps": pd.DataFrame(steps),
                "sleep": pd.DataFrame(sleep)
            }, None