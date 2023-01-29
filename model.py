# %%
import matplotlib.pyplot as plt
import numpy as np
# %%
FED_SINGLE_INCOME_BRACKETS = [
    (10275, 10),
    (41775, 12),
    (89075, 22),
    (170050, 24),
    (215950, 32),
    (539900, 35),
    (1e20, 37),
]
 
FED_MARRIED_INCOME_BRACKETS = [
    (20550, 10),
    (83550, 12),
    (178150, 22),
    (340100, 24),
    (431900, 32),
    (647850, 35),
    (1e20, 37),
]
 
def tax_progressive_bracket(income, brackets):
    tax = 0
    for i, (bracket_max, rate) in enumerate(brackets):
        prev_max = brackets[i - 1][0] if i > 0 else 0
        tax += (min(income, bracket_max) - prev_max) * rate / 100.0
        if income <= bracket_max:
            break
    return tax, tax / income
 
def tax_flat_discount(income, rate, discount):
    if income < 100:
        return - discount, -discount
    tax = income * rate / 100.0 - discount
    return tax, tax / income
 
def tax_flat(income, rate):
    return income * rate / 100.0, rate
 
def tax_us_federal(income, brackets, medicare_rate):
    if income < 100:
        return 0, 0
    income_tax = tax_progressive_bracket(income, brackets)[0]
    medicare_tax = tax_flat(income, medicare_rate)[0]
    tax = income_tax + medicare_tax
   
    return tax, tax / income

def consumption_tax(income, housing_rate, food_rate, disc_rate, luxury_rate):
    housing = min(max(600 * 12, income * 0.3), 7_500 * 12)
    tax = 0
    food = min(max(20 * 360, income * 0.15), 100 * 360)
    food = min(food, income - tax - housing)
    saving1 = income * 0.05
    saving1 = min(saving1, income - tax - housing - food)
    disc = min(max(25 * 360, income * 0.3), 3000 * 12)
    disc = min(disc, income - tax - housing - food - saving1)
    saving2 = min(income * 0.15, 25_000)
    saving2 = min(saving2, income - tax - housing - food - saving1 - disc)
    luxury = max(income * 0.05, 7500 * 12)
    luxury = min(luxury, income - tax - housing - food - saving1 - disc - saving2)
    saving3 = income - tax - housing - food - disc - saving1 - luxury - saving2

    tax = food * food_rate + housing * housing_rate + disc * disc_rate + luxury * luxury_rate
    return tax, tax / income, dict(income=income, tax=tax, housing=housing, food=food, disc=disc, saving=saving1+saving2+saving3, luxury=luxury)

def consumption_tax_ubi(income, ubi, housing_rate, food_rate, disc_rate, luxury_rate):
    tax, _, details = consumption_tax(income + ubi, housing_rate, food_rate, disc_rate, luxury_rate)
    tax = tax - ubi
    return tax, tax / income, details

if __name__ == '__main__':
    pass

# %%
l_income = np.arange(10000, 1e6, 100)
dol_rate = 0
# l_tax1 = [tax_progressive_bracket(income, FED_SINGLE_INCOME_BRACKETS)[1] for income in l_income]
l_tax1 = [tax_us_federal(income, FED_SINGLE_INCOME_BRACKETS, 6.5)[dol_rate] for income in l_income]
l_tax2 = [tax_flat_discount(income, 40, 15000)[dol_rate] for income in l_income]
l_tax3 = [consumption_tax_ubi(income, 2000, 0.025, 0.15, 0.35, 0.75)[dol_rate] for income in l_income]
plt.figure(figsize=(10, 5))
plt.plot(l_income, l_tax1, label='federal')
plt.plot(l_income, l_tax2, label='UBI')
plt.plot(l_income, l_tax3, label='Consumption')
 
plt.xscale('log')
plt.grid()
plt.legend()
plt.show()
# %%
 

import pandas as pd
num_returns = 170_000_000
percentile = pd.read_csv('income_percentile.txt', delimiter='\t')
pd.read_csv("whitespace.csv", header=None, delimiter=r"\s+")
 
per_tile = num_returns * 0.01
 
total_tax1 = list()
total_tax2 = list()
for i, row in percentile.iterrows():
    income = int(row['2022'].replace('$', '').replace(',', ''))
    tax1 = tax_us_federal(income, FED_SINGLE_INCOME_BRACKETS, 0.0)[0]
    tax2 = tax_flat_discount(income, 35, 12000)[0]
    total_tax1.append(tax1 * per_tile)
    total_tax2.append(tax2 * per_tile)
 
# print(total_tax / 1e12)
plt.plot(np.array(total_tax1).cumsum(), label='federal')
plt.plot(np.array(total_tax2).cumsum(), label='UBI')
plt.grid()
plt.legend()
# %%

l_income = np.arange(10000, 1e6, 5000)
plot_list = list()
for income in l_income:
    tax = tax_us_federal(income, FED_SINGLE_INCOME_BRACKETS, 6.5)[0]
    housing = min(max(600 * 12, income * 0.3), 7_500 * 12)
    food = min(max(20 * 360, income * 0.3), 100 * 360)
    food = min(food, income - tax - housing)
    saving1 = income * 0.075
    saving1 = min(saving1, income - tax - housing - food)
    disc = min(max(25 * 360, income * 0.3), 3000 * 12)
    disc = min(disc, income - tax - housing - food - saving1)
    saving2 = income * 0.15
    saving2 = min(saving2, income - tax - housing - food - saving1 - disc)
    luxury = income * 0.05
    luxury = min(luxury, income - tax - housing - food - saving1 - disc - saving2)
    saving3 = income - tax - housing - food - disc - saving1 - luxury - saving2

    plot_list.append(dict(income=income, tax=tax, housing=housing, food=food, disc=disc, saving=saving1+saving2+saving3, luxury=luxury))

import pandas as pd
df = pd.DataFrame(plot_list)
sofar = None
for c in df.columns:
    if c == 'income':
        continue

    if sofar is None:
        plt.bar(df['income'], df[c], width=1000)
        sofar = df[c].copy()
    else:
        plt.bar(df['income'], df[c], bottom=sofar, width=1000)
        sofar += df[c]
print(sofar)
plt.show()
print(df)
# %%
tax_us_federal(10000, FED_SINGLE_INCOME_BRACKETS, 6.5)
# %%

plt.bar(x=[1e5, 1e6], height=[1,2], width=50000)
plt.show()
# %%
df['housing'].to_numpy()[:2]
# %%
df['housing'].to_numpy()[:5]
# %%


# %%
consumption_tax_ubi(2e5, 5000, 0.025, 0.15, 0.35, 0.5)
# %%
tax_us_federal(4e5, FED_SINGLE_INCOME_BRACKETS, 0)
# %%
