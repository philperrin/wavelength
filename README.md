# Slack App HomeDemo 
Leveraging the App Home feature

_Updated: January, 2020_<br>
_Published October, 2019_

---

There are two code samples to achieve the same app: 
- The sample code with Node w/ Express: this repo
- The sample code with Slack **Bolt**: [https://glitch.com/edit/#!/apphome-bolt-demo-note](https://glitch.com/edit/#!/apphome-bolt-demo-note)

## Tutorial
[https://api.slack.com/tutorials/app-home-with-modal](https://api.slack.com/tutorials/app-home-with-modal)

---

## Slack App Config

Go to https://api.slack.com/apps to create a new app. 

- App Home
  - Enable Home Tab
  - Enable Message (if your app takes DM from users)
  
- Enable Bot user

- Add appropriate bot scope(s)
  - `chat.write` (*Note: you actually do not need this scope for this sample app, but do need to add one to be able to install the app!*)

- Enable Events
  - Request URL should be `https://your-project.glitch.me/slack/events`
  - Subscribe to workspace events
  - Add `app_home_opened`
  - Save
  
- Go to **Interactivity & Actions** and enable
  - Reuest URL should be: `https://your-project.glitch.me/slack/actions`
  - Save
  
  
On Slack client:
  - Click the app name to go to the home tab
  - Click the "Add a stickie" button and see what happens!
  