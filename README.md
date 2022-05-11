Code is free to use

Find all tweets by search words for all the time with selenium

All u have to do is

                 1)have geckodriver 

                 2)have redis (for docker users "docker run -d -p 6379:6379 redis")

                 3)install requirements.txt with "pip install -r requirements.txt"

                 4)run celery with "celery -A worker.celery worker  --loglevel=info -f celery.log --concurrency=1" 
                 (concurrency max value is max logc cpu)

                 5)run for example "python3 main.py -f cat_vega  -s 'cat vega' -d '3'"

                                                    where -f is a file (out) in csv format automatically

                                                          -s is a search string

                                                          -d days from now per one iteration 
                                                          in cycle to the first day of twitter

U can also edit main.py and use commented code to search for companies from companies.csv using concurrency>1 

and edit selenium_twitter.py where u can find commented login func (works but u can face captcha and it'll ruin ur code)
       
