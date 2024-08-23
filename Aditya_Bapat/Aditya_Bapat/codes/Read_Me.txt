Read Me:

file.py:
Start of operation by taking ticker and recording Investment, Remaining Cash, Total Cash on signals like Buy, Sell, Short Sell and Buy Hold.

buy_sell_signals.py:
Record Buy-Sell and Sell-Buy pairs with their Highest and Lowest Investment and percentage. 

average.py:
By help of buy_sell_signals.py file we record a average percentage of each row, by the help of avg percentage we create a threshold condition that if transaction row's percentage >= highest (Buy Hold) /lowest (Short Sell) then it sells half of the shares.

buy-sell_analysis.py:
We record the buy-sell pairs and by comparing start and end total cash of each pairs we determine if the pair is profitable or not.

charge.py:
We add buy and sell charge to the average output file.

comparison_avg_without-avg.py:
i) End Total Cash value from file and average file.
ii) Percentage change of Total Cash from both datasets.
iii) Comparison of both Datasets throught line chart.

anual_interest.py:
Calculate Anual Interest on charge

local_maxima 
local minima

if local_maxima > previous_local_maxima:
    calculate local minima from date of new-local_maxima
elif local_maxima < previous_local_maxima:
    Calculate local minima from date of local_maxima

where min value of new local minima is stored, only include that record, rest of record no need to append