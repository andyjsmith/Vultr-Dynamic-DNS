# Vultr Dynamic DNS
### Dynamically update IP addresses in Vultr DNS without services like No-IP
If you want to map an A record in Vultr's DNS to a local machine but you aren't paying your ISP for a static IP, use this service to automatically update an IP change in Vultr. Since Vultr does not provide a Dynamic DNS service, programs like ddclient cannot be used, so this is an alternative. It uses [Vultr's API](https://www.vultr.com/api/) and simple GET and POST requests, and uses an API key opposed to your username and password.

# Basic Setup
- First, [set up your domain to use Vultr's DNS service](https://www.vultr.com/docs/introduction-to-vultr-dns) if you haven't already. You will need access to your domain registrar to point your domain to Vultr's nameservers. After this is done you can set up your DNS records in Vultr, so add all of the necessary A, CNAME, TXT, MX, etc. records you need and then continue with this guide.
- Once you have set up Vultr DNS, go to [Vultr DNS](https://my.vultr.com/dns/) and click on your domain name in this list. Note which records you would like to be dynamically updated. Only A records are supported by this utility. If you have multiple A records that you want updated to the same IP address, change them to CNAMEs and point them to one A record. This will simplify things for you in the long run and is considered the proper way to configure DNS.
- Install Python 3
    - [Linux](http://python-guide-pt-br.readthedocs.io/en/latest/starting/install3/linux/)
    - [Mac OSX](http://python-guide-pt-br.readthedocs.io/en/latest/starting/install3/osx/)
    - [Windows](http://python-guide-pt-br.readthedocs.io/en/latest/starting/install3/win/)
- Clone this repository: `git clone https://github.com/andyjsmith/Vultr-Dynamic-DNS.git vultrddns && cd vultrddns`
- Fill out config.json. Read the intructions in config.json.example, you will need to generate an API key in Vultr. It is important to click "Allow All IPv4".
- Test the script and configuration: `python3 ddns.py`. If there aren't any errors, the setup is complete.

## Known Issues
- If you get an error stating your IP is not authorized, you must go to your Vultr account, click on your name in the top right and click API. You can then go to Access Control and click "Allow All IPv4" and/or "Allow All IPv6", or manually specify your IP. This step is important as IPv6 may not be enabled by default but some computers will communicate on IPv6 by default.

# Automation
After completing the basic setup, it is important to set up a recurring task as the script does not do this by default.
### Linux & Mac OSX
- Find the full path of the ddns.py file using `realpath ddns.py`
- Run `crontab -e`
- Add the following line to the end of the file, adding in the real path to the ddns.py file: `*/30 * * * * cd [full path to ddns.py] && python3 ddns.py > /dev/null 2>&1`. This will run the script every 30 minutes and redirect all of its output to /dev/null.
- Save and quit out of the text editor. The crontab file will automatically be install and your IP will now automatically be updated.
### Windows
Create a task in Task Scheduler to run every 30 minutes.
Follow the [Microsoft guide](https://technet.microsoft.com/en-us/library/cc748993(v=ws.11).aspx) for basic task creation.
- Open task scheduler and click "Create Task..."
- Give it a name and create a new trigger
- Click "Daily" and under Advanced Settings click to repeat the task every 30 minutes and change "for a duration of" to "Indefinitely"
- Add a new action to start a program and browse to your python executable. Add the ddns.py script as an argument.
