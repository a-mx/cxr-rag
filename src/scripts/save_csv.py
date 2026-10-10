from pathlib import Path
import pandas as pd

def get_image_path(root: str, subject_id: str, study_id: str, dicom_id: str):
    root = Path(root)
    files = root.joinpath("files")

    prefix = f"p{subject_id[:2]}"
    subject_id = f"p{subject_id}"
    study_id = f"s{study_id}"
    dicom_id = f"{dicom_id}.jpg"

    path = files.joinpath(prefix).joinpath(subject_id).joinpath(study_id).joinpath(dicom_id)
    return path

def get_report_path(root: str, subject_id: str, study_id: str):
    root = Path(root)
    files = root.joinpath("files")

    prefix = f"p{subject_id[:2]}"
    subject_id = f"p{subject_id}"
    study_id = f"s{study_id}.txt"

    path = files.joinpath(prefix).joinpath(subject_id).joinpath(study_id)
    return path

def save_reports(df, mimic_cxr_path, data_path):
    df = df.copy()
    to_drop = [
            "StudyTime",
            "StudyDate",
            "Rows",
            "Columns",
            "PerformedProcedureStepDescription",
            "ProcedureCodeSequence_CodeMeaning",
            "ViewPosition",
            "PatientOrientationCodeSequence_CodeMeaning",
            "dicom_id",
            "ViewCodeSequence_CodeMeaning"
            ]

    df = df.drop(to_drop, axis=1)
    df = df[~df.duplicated(subset='study_id', keep='first')]

    df['path'] = df.apply(lambda row: get_report_path(
            root=mimic_cxr_path.joinpath('mimic-cxr-reports'),
            subject_id=row['subject_id'],
            study_id=row['study_id']),
            axis=1)

    df = df.reset_index(drop=True)

    filename = "reports.csv"
    df.to_csv(data_path.joinpath('csv').joinpath(filename))

def save_photos(df, mimic_cxr_path, data_path):
    df = df.copy()
    to_drop = [
            "StudyTime",
            "StudyDate",
            "Rows",
            "Columns",
            "PerformedProcedureStepDescription",
            "ProcedureCodeSequence_CodeMeaning",
            "ViewPosition",
            "PatientOrientationCodeSequence_CodeMeaning",
            ]

    df = df.drop(to_drop, axis=1)

    df['path'] = df.apply(lambda row: get_image_path(
            root=mimic_cxr_path,
            subject_id=row['subject_id'],
            study_id=row['study_id'],
            dicom_id=row['dicom_id']),
            axis=1)

    df = df.reset_index(drop=True)

    filename = "photos.csv"
    df.to_csv(data_path.joinpath('csv').joinpath(filename))

def save(df, mimic_cxr_path, data_path):
    save_reports(df, mimic_cxr_path, data_path)
    save_photos(df, mimic_cxr_path, data_path)

def main():
    data_path = Path.cwd().joinpath("data")
    raw_path = data_path.joinpath("raw")
    mimic_cxr_path = raw_path.joinpath("mimic-cxr")
    metadata_filename = 'mimic-cxr-2.0.0-metadata.csv'
    df = pd.read_csv(mimic_cxr_path.joinpath(metadata_filename), dtype=str)

    save(df, mimic_cxr_path, data_path)
    
if __name__ == "__main__":
    main()