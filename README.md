# pucauto

A Pucatrade bot that will automatically accept trades for you.

pucauto is a Python script that uses Selenium to launch a Firefox instance and log you in to Pucatrade. The
script then refreshes the Trades page every 5 seconds looking for a "Send Card" button. If it finds one, it
will click the button and then complete the trade for you. You can leave pucauto running in the background of
your computer while you do other things or when you're sleeping or at work.

Now I need to build a bot to fill out envelopes...

![too-many-envelopes](http://i.imgur.com/S9ZHiO3.jpg)

### Installation

#### Prerequisites

1. Git
2. Python
3. Pip
4. Firefox

Most Macs come with most of this stuff already installed. If you're on Windows, I'm not sure what to do. Can someone
contribute to this repo and help me write some Windows instructions?

#### Steps

1. Clone this repository with `git clone https://github.com/tomreece/pucauto.git` or download and unzip the .zip using the link over on the right --->.
2. Open Terminal.
3. Go to the pucauto folder you just cloned or downloaded.
3. Run `sudo pip install -r requirements.txt` and enter your system password when prompted.

### Running

After you have followed the installation steps, you can run pucauto with:

`python pucauto.py youremailaddress@gmail.com yourpucatradepassword`

### Advanced Usage

If you have a cloud server somewhere like Rackspace, AWS, Linode, etc you can run the script there. You'll just need to install Firefox, Xvfb, and tmux. This is how I run mine on a Rackspace Ubuntu instance.

1. ssh in to your server
1. `apt-get install firefox xvfb tmux git` to install dependencies
1. `git clone https://github.com/tomreece/pucauto.git` to clone this repository
1. `cd pucauto`
1. `Xvfb &` to start Xvfb in the background
1. `export DISPLAY=:0` so Firefox knows which Xvfb display to use
1. `tmux` to start a tmux session which will continue to run when you disconnect from the server
1. `python pucauto.py youremailaddress@gmail.com yourpucatradepassword` to start pucauto
1. If you get no error messages, then everything is working.
1. `ctrl + b then press d` to detach from the tmux session (it will continue to run)
1. You can now exit your ssh session to the server.
1. When you reconnect to the server later, `tmux at` to re-attach to the tmux session you started earlier and pucauto will still be running.
1. After a few days of running, Firefox seems to continually eat up more and more memory so you may need to stop `python pucauto.py` and start it again.

### FAQ

* Why do I have to provide my Pucatrade username and password? Is this safe?
    * The bot types your username and password into the proper fields on the Pucatrade page. You can see this happening in `pucauto.py` on line 20. Your username and password are not used for anything else. That's why this project is open source, so you can see the code and know roughly what's happening even if you're not a developer.
* How do I run this on Windows?
    * I have a collaborator working on Windows instructions. They should be added to this README soon. Check back.
* This is too difficult for me, but the bot sounds useful. Can you run it for me?
    * Yes. Email me at tomreece[at]gmail.com and we'll talk.

### Help

If you have any questions, feel free to reach out to me on Twitter @tomreece or tomreece[at]gmail.com

If the above instructions are too complicated and you are still interested in using pucauto, hit me up at tomreece[at]gmail.com and we can talk. I would be willing to run the bot for you against your Pucatrade account if you cover the small server cost of $5 a month. I'll let you try for a week before you pay.
