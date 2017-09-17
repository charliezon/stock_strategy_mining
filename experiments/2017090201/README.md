# Purpose

Check if the profit rate, increase rate, turnover rate and big index related information are effective when they are used to classify *follow* signal with XGBoost.

# Parameters

* stop_loss_rate: 10% (0.100)
* take_profit_rate: 3.4% (0.034)
* holding_days: 30
* lose_cache: 0.5% (0.005)

# Extracted features after preprocessing

* 1. Whether Shanghai index (999999) is greater than MA20
* 2. Whether Shenzhen index (399001) is greater than MA20
* 3. Whether gravity of both Shanghai index and Shenzhen index increase compared with previous trading day
* 4. Whether close prices of both Shanghai index and Shenzhen index greater than open prices, and greater than close prices and open prices of previous trading day  
* 5. Whether profit rate greater than 90%
* 6. Whether profit rate is between (60%, 90%]
* 7. Whether profit rate is between (30%, 60%]
* 8. Whether profit rate is between (25%, 30%]
* 9. Whether profit rate is between (20%, 25%]
* 10. Whether profit rate is between (15%, 20%]
* 11. Whether profit rate is between (10%, 15%]
* 12. Whether profit rate is between (5%, 10%]
* 13. Whether profit rate is between [0%, 5%]
* 14. Whether turnover rate is less than 0.5%
* 15. Whether turnover rate is between (0.5%, 1%]
* 16. Whether turnover rate is between (1%, 3%]
* 17. Whether turnover rate is between (3%, 5%]
* 18. Whether turnover rate is between (5%, 10%]
* 19. Whether turnover rate is between (10%, 20%]
* 20. Whether turnover rate is greater than 20%
* 21. Whether increase rate is not greater than 0%
* 22. Whether increase rate is between (0%, 2%]
* 23. Whether increase rate is between (2%, 4%]
* 24. Whether increase rate is between (4%, 6%]
* 25. Whether increase rate is between (6%, 9%]
* 26. Whether increase rate is greater than 9%