# SUBASTAS BOE

These codes are based on webscrapping with Python, specifically with Selenium and BeautifulSoup. 

There are three main functionalities deployed: 
-	Retrieval of all the existing auctions (opened and/or closed) for a specific province 
-	Delivery of daily emails with new auctions
-	Tracking of the biddings 

## Retrieval of the existing auctions
The code to implement this functionality is getData.py and it is settled to Madrid by default. 
The code extracts the auctions and its data from the site and stores it in a json file. Afterwards, it is cleaned and stored in an Excel file to simplify its use and to have the data both in relational and non-relational formats. 
It has deployed an incremental load, if you have already executed the code beforehand, it only downloads auctions that are not in the files to avoid duplicities and to minimize execution times. 
The final bidding price is contained in _PRECIO_PUJA_ variable in the dataset.
To retrieve data from other provinces, you need to change the url_base.txt file where you should copy the URL for the search you want to get. To make the URL valid, you need to remove the 0-50 from the end. The following URL will be transformed into a valid one:
URL from the site: [https://subastas.boe.es/subastas_ava.php?accion=Mas&id_busqueda=_S2lpeStKeEJ3ZUlFS2VhbWk3NXJHNDljMk9ySitSZXhYNmc3R2dESSsyZXhCNEtHUlcxbjd2NkdRT24rUVlmVkQyMUwrb3RUQzBwaDQrY3RmREU0UTBzWE5hYllQSCtSSDQ3MzZtNm10YlJLVUk3M1hZNzdvVWloaXg5cWJZSWlLK2dHSnM0alAzejRCSlR0Z0Q1Mm0wYmRyNThjN3FSMG9rcnJka2dSOGFjZWJNbSswejBvNVdSak9xUFFGZ3E0MVIzMU9rZWhXSitCWWlYQkRHdnAzYUtDbHFrYVVwdnduMDdTK2p3M1pSdk4xOU00Z1hzSmRoR3p2YzJ3eFd2dlc4TGFrU3NKeWVOQUpmNEtYZU1PbEttTk15VzRKY1ZzRW5idEJiTWwvMklXWjhkZ1dkaVVJTTNlZ0s4M2VQQWQraDJtNFoxc1hBSVR3eXB6UkxsNkhBPT0,-0-50]
Valid URL:
[https://subastas.boe.es/subastas_ava.php?accion=Mas&id_busqueda=_S2lpeStKeEJ3ZUlFS2VhbWk3NXJHNDljMk9ySitSZXhYNmc3R2dESSsyZXhCNEtHUlcxbjd2NkdRT24rUVlmVkQyMUwrb3RUQzBwaDQrY3RmREU0UTBzWE5hYllQSCtSSDQ3MzZtNm10YlJLVUk3M1hZNzdvVWloaXg5cWJZSWlLK2dHSnM0alAzejRCSlR0Z0Q1Mm0wYmRyNThjN3FSMG9rcnJka2dSOGFjZWJNbSswejBvNVdSak9xUFFGZ3E0MVIzMU9rZWhXSitCWWlYQkRHdnAzYUtDbHFrYVVwdnduMDdTK2p3M1pSdk4xOU00Z1hzSmRoR3p2YzJ3eFd2dlc4TGFrU3NKeWVOQUpmNEtYZU1PbEttTk15VzRKY1ZzRW5idEJiTWwvMklXWjhkZ1dkaVVJTTNlZ0s4M2VQQWQraDJtNFoxc1hBSVR3eXB6UkxsNkhBPT0,-]
This code is automated using a Raspberry Pi (cron jobs) to be executed daily.

## Delivery of daily emails
This functionality is deployed in the code sendEmail.py, you can configure the possibility of sending an email with updates. This functionality will send an email with auctions that you have retrieved in the execution but were not in the json file before. Before executing it, it is necessary to define:
-	The credentials of the sending email
-	The list of emails to send the email

### The credentials of the sending email:
It is necessary to write the email and password of the email from you want to send the email. You need to fill a file named email_credentials.txt where you write the email on the first row and the password on the second.

### The list of emails to send the email:
You need to fill a file named emails.txt where you write each email on a row. 
To enable this functionality in your Google account (sending email), you need to change the privacy configuration following these four steps:
-	Go to Manage your Google account
-	Select Security tab
-	Go to Unsafe application access
-	Enable access
This code is automated using a Raspberry Pi (cron jobs) to receive daily emails with the updates.

## Tracking of the biddings
The code that implements this functionality is login.py, you can see what the last bid of certain auctions is.  
Beforehand, you need to fill two documents with:
-	Email and password to access the site
-	Auctions to follow their biddings

### Email and password:
To be able to use this functionality, you need to fill a file named credentials.txt where you write the email on the first row and the password on the second. Only registered users can see biddings while the auction is active. 

### Auctions to follow: 
You need to fill a file named subastas_following.txt where you write each auction id on a row. 
After getting the bidding data of the auctions you are following, an email is sent with the evolution of the bids. As it happens with sendEmail.py code, before executing it, it is necessary to define: the credentials of the sending email and the list of emails to send the email. 
The credentials of the sending email: It is necessary to write the email and password of the email from you want to send the email. You need to fill a file named email_credentials.txt where you write the email on the first row and the password on the second.
The list of emails to send the email: You need to fill a file named emails.txt where you write each email on a row. 
This code is also automated using a Raspberry Pi (cron jobs) to receive emails with the updates at 4 different hours every day.




```markdown
Syntax highlighted code block


**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).


