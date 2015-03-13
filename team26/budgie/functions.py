from datetime import datetime
import calendar

def list_of_months_years(number):
	today = datetime.now()
	months_all = []
	year_for_month = today.year
	months = []
	years = []
	month_year = []
	for i in range(number):
		if i == 0:
			todays_month = today.month + 1
		else:
			todays_month = months_all[i-1]
		months_all.append((todays_month - 1)%12) if (todays_month - 1)%12 != 0 else months_all.append(12)
		if months_all[i] == 12:
			year_for_month = year_for_month - 1 
		years.append(year_for_month)
		temp = calendar.month_name[months_all[i]] + " " + str(years[i])
		month_year.append(temp)
	
	months = months_all[::-1]
	years = years[::-1]
	month_year = month_year[::-1]
	return months, years, month_year

    
