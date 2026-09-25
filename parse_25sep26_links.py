import json
import re

raw_text = """
Submission
Test Name
Est Comp. Date
Rush
Status
[ETX-260914-0288](https://etrax.eagleanalytical.com/Submission/Details/orwVoxfl80D3mOUCRnY%24IA__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/9skbGZ%24OxO2lE%24JVQa9TFQ__) [T0001118694]
9/25/2026
Data Review
[ETX-260914-0485](https://etrax.eagleanalytical.com/Submission/Details/edvAnLwR-qKQOn8Y5BjYaA__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/13Hwg7chz7l%24Dd1Yf5oVeA__) [T0001119084]
9/25/2026
Data Review
[ETX-260914-0534](https://etrax.eagleanalytical.com/Submission/Details/dtRjACB11SxwliUsAhHEPw__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/TqjeqBLcGcYuU3thylzuyQ__) [T0001119180]
9/25/2026
Data Review
[ETX-260915-0493](https://etrax.eagleanalytical.com/Submission/Details/TfQ0kflITPnLLlD7EIl0ow__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/g5JbGPtMMYshKpHHHMDfiA__) [T0001121218]
9/25/2026
Data Review
[ETX-260915-0606](https://etrax.eagleanalytical.com/Submission/Details/ttWajUFcl%24RqbIBiKUfV0g__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/-TEZr0-M8D6i50lMQTuV8g__) [T0001121492]
9/25/2026
Data Review
[ETX-260916-0225](https://etrax.eagleanalytical.com/Submission/Details/EIHm-8wLXQAN8-I%24NigK6Q__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/MJ1WlHbjnPSFCf3SHC0oNw__) [T0001122875]
9/25/2026
Data Review
[ETX-260916-0404](https://etrax.eagleanalytical.com/Submission/Details/Vw-Y7-jKBkN2TmZ2LeUILA__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/Mi6T%24%24hvwNHqwjHeb38VVA__) [T0001123638]
9/25/2026
Data Review
[ETX-260916-0493](https://etrax.eagleanalytical.com/Submission/Details/ANCdS0jioD0zR8N15RYo7w__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/jxpVd4ax1xTw1fdWyaQF2Q__) [T0001123835]
9/25/2026
Data Review
[ETX-260916-0513](https://etrax.eagleanalytical.com/Submission/Details/UsHQoHVXYWlSNQzZ34qDjw__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/Pgb7Levgvxy-MRW2S27wtQ__) [T0001123903]
9/25/2026
Data Review
[ETX-260916-0774](https://etrax.eagleanalytical.com/Submission/Details/9sIE6PAUJ5Fu9EAGYOg67Q__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/GY-PfLFWHR1bv7wsQgdbkQ__) [T0001124730]
9/25/2026
Data Review
[ETX-260916-0865](https://etrax.eagleanalytical.com/Submission/Details/ENBTjvX0xLHj7MLhahHnZQ__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/2BUqF%24ELpqX7ak01tcva4w__) [T0001125088]
9/25/2026
Data Review
[ETX-260917-0214](https://etrax.eagleanalytical.com/Submission/Details/AbU7aABUXXHyEWDbQGX5ig__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/FqpEOBMl-VgPjfzTWkxXqw__) [T0001125547]
9/28/2026
Data Review
[ETX-260917-0253](https://etrax.eagleanalytical.com/Submission/Details/7HgaqMty7xvzmVlbjjnH7w__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/crPHxVwVZdo0rcZK%24VKvGw__) [T0001125631]
9/25/2026
Data Review
[ETX-260917-0336](https://etrax.eagleanalytical.com/Submission/Details/t-7BD35sytP2EBjNb8ZssQ__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/oTRYi8tV2we-aam4LQzgNA__) [T0001125894]
9/25/2026
Data Review
[ETX-260917-0392](https://etrax.eagleanalytical.com/Submission/Details/E15tQE0-V1mWbosWRgROSQ__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/rWckBLb0LWr5W0ZnJJHq3A__) [T0001126014]
9/25/2026
Data Review
[ETX-260917-0403](https://etrax.eagleanalytical.com/Submission/Details/nMIAp3U0SPlwSJLNvlJOxQ__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/6EU3cG4BAks8YJzOtHFFpg__) [T0001126044]
9/25/2026
Data Review
[ETX-260917-0411](https://etrax.eagleanalytical.com/Submission/Details/ScrckFi%24aL%24B7w7qbE6N%24g__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/rtjjFq4Vc7CSxXbjEEG1tw__) [T0001126052]
9/28/2026
Data Review
[ETX-260917-0429](https://etrax.eagleanalytical.com/Submission/Details/zV3J0Z4ZlQQsLLtdUzfqrA__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/HopV%24m6twgKGcp1hx1-oxw__) [T0001126112]
9/28/2026
Data Review
[ETX-260917-0648](https://etrax.eagleanalytical.com/Submission/Details/cGHltu93d6wWmtGm63aPXQ__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/UgOV0r7wbZUfGTztSkZMdA__) [T0001126647]
9/25/2026
Data Review
[ETX-260917-0659](https://etrax.eagleanalytical.com/Submission/Details/9Qu9Lu2RGdg-si9SSsV%24GQ__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/V8fvSrZHkwDPpiYXyHJIkQ__) [T0001126662]
9/28/2026
Data Review
[ETX-260917-0663](https://etrax.eagleanalytical.com/Submission/Details/yDRvj2i3utqBbyXMWO4EQA__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/tZVPiKg9bZoPuM7JmbjGew__) [T0001126667]
9/28/2026
Data Review
[ETX-260917-0667](https://etrax.eagleanalytical.com/Submission/Details/O0FSXOxga5SRsje6b8-GAA__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/xtjZVStrvzwmWFA-4s9VLQ__) [T0001126673]
9/28/2026
Data Review
[ETX-260917-0753](https://etrax.eagleanalytical.com/Submission/Details/lEO-0xovN0f3IrrX4JZ2rw__)
[Celsis Sterility Test](https://etrax.eagleanalytical.com/SubmissionTest/Details/Ese1QwQ3W1vQPFbh73zGqg__) [T0001126974]
9/28/2026
Data Review
"""

pattern = re.compile(
    r'\[(ETX-\d{6}-\d{4})\]\((https://etrax\.eagleanalytical\.com/Submission/Details/[^\)]+)\)\s*'
    r'\[Celsis Sterility Test\]\((https://etrax\.eagleanalytical\.com/SubmissionTest/Details/[^\)]+)\)\s*\[(T\d+)\]\s*'
    r'(\d+/\d+/\d{4})\s*'
    r'([A-Za-z ]+)',
    re.MULTILINE
)

matches = pattern.findall(raw_text)
print(f"Extracted {len(matches)} links!")

links = []
for m in matches:
    sid, sub_url, test_url, titan_id, est_date, status = m
    links.append({
        "Sample": sid,
        "url": test_url,
        "submission_url": sub_url,
        "titan_id": titan_id,
        "est_comp_date": est_date,
        "initial_status": status.strip()
    })

with open("celsis_250926_links.json", "w", encoding="utf-8") as f:
    json.dump(links, f, indent=2, ensure_ascii=False)

print("Saved celsis_250926_links.json successfully!")
