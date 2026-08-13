import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# FUNNEL ANALYSIS & DROP-OFF DETECTION
# ==========================================

# Load dataset
df = pd.read_csv("data/raw/customer_funnel.csv")

# ==========================================
# TASK 1: DEFINE FUNNEL STAGES
# ==========================================

stage1_signup = len(df[df["signup_completed"] == 1])
stage2_email = len(df[df["email_entered"] == 1])
stage3_password = len(df[df["password_created"] == 1])
stage4_verified = len(df[df["email_verified"] == 1])
stage5_payment = len(df[df["payment_added"] == 1])
stage6_purchase = len(df[df["first_purchase"] == 1])

stages = {
    "Sign Up": stage1_signup,
    "Email Entered": stage2_email,
    "Password Created": stage3_password,
    "Email Verified": stage4_verified,
    "Payment Added": stage5_payment,
    "First Purchase": stage6_purchase
}

print("\nFUNNEL STAGES")
print("=" * 50)

for stage, count in stages.items():
    print(f"{stage}: {count}")


# ==========================================
# TASK 2: CALCULATE DROP-OFF
# ==========================================

stage_list = list(stages.values())
stage_names = list(stages.keys())

drop_off = []

for i in range(len(stage_list) - 1):

    users_before = stage_list[i]
    users_after = stage_list[i + 1]

    users_lost = users_before - users_after

    drop_pct = (users_lost / users_before) * 100
    completion_pct = (users_after / users_before) * 100

    drop_off.append({
        "from_stage": stage_names[i],
        "to_stage": stage_names[i + 1],
        "users_lost": users_lost,
        "completion_rate": completion_pct,
        "drop_rate": drop_pct
    })

funnel_df = pd.DataFrame(drop_off)

print("\nDROP-OFF ANALYSIS")
print("=" * 70)
print(funnel_df.to_string(index=False))


# Find biggest drop
biggest_drop_idx = funnel_df["users_lost"].idxmax()

biggest_drop = funnel_df.loc[biggest_drop_idx]

print("\nBIGGEST DROP")
print("=" * 50)
print(f"From: {biggest_drop['from_stage']}")
print(f"To: {biggest_drop['to_stage']}")
print(f"Users Lost: {biggest_drop['users_lost']}")
print(f"Drop Rate: {biggest_drop['drop_rate']:.1f}%")


# ==========================================
# TASK 3: CREATE FUNNEL CHART
# ==========================================

plt.figure(figsize=(12, 6))

plt.bar(
    stages.keys(),
    stages.values()
)

plt.xlabel("Funnel Stage")
plt.ylabel("Number of Users")
plt.title("Signup Funnel: Users at Each Stage")

plt.xticks(rotation=45, ha="right")

# Add numbers above bars
for i, count in enumerate(stages.values()):
    plt.text(
        i,
        count,
        str(count),
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    "output/funnel_chart.png",
    dpi=150
)

plt.show()

print("\nFunnel chart saved successfully.")


# ==========================================
# TASK 4: BUSINESS IMPACT
# ==========================================

revenue_per_customer = 100

impact_analysis = []

for index, row in funnel_df.iterrows():

    users_lost = row["users_lost"]

    revenue_lost = users_lost * revenue_per_customer

    impact_analysis.append({
        "drop_point": f"{row['from_stage']} -> {row['to_stage']}",
        "users_lost": users_lost,
        "revenue_impact": revenue_lost
    })

impact_df = pd.DataFrame(impact_analysis)

impact_df = impact_df.sort_values(
    "revenue_impact",
    ascending=False
)

print("\nBUSINESS IMPACT")
print("=" * 70)
print(impact_df.to_string(index=False))


# ==========================================
# TASK 5: RECOMMENDATION
# ==========================================

highest_impact = funnel_df.loc[
    funnel_df["users_lost"].idxmax()
]

users_lost = highest_impact["users_lost"]

revenue_impact = users_lost * revenue_per_customer

recommendation = f"""

FUNNEL OPTIMIZATION PRIORITY
============================

Critical Bottleneck:
{highest_impact['from_stage']} -> {highest_impact['to_stage']}

Users Lost:
{users_lost}

Drop Rate:
{highest_impact['drop_rate']:.1f}%

Revenue Impact:
${revenue_impact:,.0f}

Possible Reasons:
- The step may be confusing.
- The step may be too complicated.
- There may be too many fields.
- Users may not understand what to do.

Recommended Action:
Simplify this step and run an A/B test.

Success Criteria:
Monitor the drop-off rate after the change.
If conversion improves, the change can be rolled out.

"""

print(recommendation)


# ==========================================
# SAVE ANALYSIS
# ==========================================

with open(
    "output/funnel_analysis.txt",
    "w"
) as file:

    file.write("FUNNEL ANALYSIS REPORT\n")
    file.write("=" * 50 + "\n\n")

    file.write("STAGES:\n")

    for stage, count in stages.items():
        file.write(f"{stage}: {count}\n")

    file.write("\nDROP-OFF ANALYSIS:\n")
    file.write(funnel_df.to_string(index=False))

    file.write("\n\nBUSINESS IMPACT:\n")
    file.write(impact_df.to_string(index=False))

    file.write("\n")
    file.write(recommendation)

print("\nAnalysis report saved successfully.")