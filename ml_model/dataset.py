
import pandas as pd

data = {
    "text": [
        # REAL examples: ordinary, plausible news claims
        "The election commission announced the official voting schedule.",
        "The national space agency announced a satellite launch.",
        "The health department published its annual public health report.",
        "The city council approved a budget for road repairs.",
        "The weather department issued a heavy rainfall warning.",
        "The university announced its examination timetable.",
        "The railway department announced a new train service.",
        "The government released its annual economic report.",

        # FAKE examples: extraordinary claims requiring strong evidence
        "Drinking ordinary water cures every known disease.",
        "The government will give every citizen free gold tomorrow.",
        "Humans can survive indefinitely without oxygen.",
        "Eating one fruit makes people immune to every virus.",
        "A secret machine can create unlimited free electricity.",
        "Every student will receive one million rupees tomorrow.",
        "Scientists say the moon is made entirely of cheese.",
        "A magic pill guarantees instant success in every exam."
    ],
    "label": [
        "REAL", "REAL", "REAL", "REAL",
        "REAL", "REAL", "REAL", "REAL",
        "FAKE", "FAKE", "FAKE", "FAKE",
        "FAKE", "FAKE", "FAKE", "FAKE"
    ]
}

df = pd.DataFrame(data)

print(df)
print("\nDataset created successfully!")
print("Number of examples:", len(df))
print("\nLabel counts:")
print(df["label"].value_counts())
