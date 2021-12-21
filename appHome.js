const axios = require("axios");
const qs = require("qs");

const JsonDB = require("node-json-db");
const db = new JsonDB("notes", true, false);

const apiUrl = "https://slack.com/api";

//db.delete("/");

/*
 * Home View - Use Block Kit Builder to compose: https://api.slack.com/tools/block-kit-builder
 */

const updateView = async user => {
  // Intro message -

  let blocks = [
    {
      type: "header",
      text: {
        type: "plain_text",
        text: "Utilization Reporter",
        emoji: true
      }
    },
    {
      type: "section",
      text: {
        type: "mrkdwn",
        text:
          "This app will retrieve an image from our Tableau Online utilization report. \n" +
          "If you have any questions, please contact <@U01SBRDSDFU> or <@UGWATNN22>. \n" +
          "Your userid is " +
          `${user}`
      }
    },

    /*
    This section can be used if we want the reporter to activate on a button rather than showing up via app.
    {
      type: "actions",
      elements: [
        {
          type: "button",
          text: {
            type: "plain_text",
            text: "Retrieve Utilization Report",
            emoji: true
          },
          action_id: "utilization"
        }
      ]
    },
    */

    {
      type: "divider"
    },
    {
      type: "image",
      image_url:
        "https://cdn.glitch.me/31417829-9685-4c0a-af4f-74670d92c900%2F"+`${user}`+".png",
      alt_text: "inspiration"
    },
    {
        type: "section",
        text: {
          type: "mrkdwn",
          text:
            "To view this report online, please <https://prod-useast-b.online.tableau.com/#/site/tessellationhq/views/ProjectReporting/BillableUtilization|click here>."
        }
      }
  ];

  // Append new data blocks after the intro -

  let newData = [];

  try {
    const rawData = db.getData(`/${user}/data/`);

    newData = rawData.slice().reverse(); // Reverse to make the latest first
    newData = newData.slice(0, 50); // Just display 20. BlockKit display has some limit.
  } catch (error) {
    //console.error(error);
  }

  if (newData) {
    let noteBlocks = [];

    for (const o of newData) {
      const color = o.color ? o.color : "yellow";

      let note = o.note;
      if (note.length > 3000) {
        note = note.substr(0, 2980) + "... _(truncated)_";
        console.log(note.length);
      }

      noteBlocks = [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: note
          },
          accessory: {
            type: "image",
            image_url: `https://cdn.glitch.com/0d5619da-dfb3-451b-9255-5560cd0da50b%2Fstickie_${color}.png`,
            alt_text: "stickie note"
          }
        },
        {
          type: "context",
          elements: [
            {
              type: "mrkdwn",
              text: o.timestamp
            }
          ]
        },
        {
          type: "divider"
        }
      ];
      blocks = blocks.concat(noteBlocks);
    }
  }
  // The final view -

  let view = {
    type: "home",
    title: {
      type: "plain_text",
      text: "Keep notes!"
    },
    blocks: blocks
  };

  return JSON.stringify(view);
};

/* Display App Home */

const displayHome = async (user, data) => {
  if (data) {
    // Store in a local DB
    db.push(`/${user}/data[]`, data, true);
  }

  const args = {
    token: process.env.SLACK_BOT_TOKEN,
    user_id: user,
    view: await updateView(user)
  };

  const result = await axios.post(
    `${apiUrl}/views.publish`,
    qs.stringify(args)
  );

  try {
    if (result.data.error) {
      console.log(result.data.error);
    }
  } catch (e) {
    console.log(e);
  }
};

/* Open a modal */

const openModal = async (trigger_id, user) => {
  const u_id = { user };

  const modal = {
    type: "modal",
    title: {
      type: "plain_text",
      text: "Report:"
    },
    blocks: [
      {
        type: "image",
        image_url:
          "https://images.unsplash.com/photo-1544526226-d4568090ffb8?ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8aGQlMjBpbWFnZXxlbnwwfHwwfHw%3D&ixlib=rb-1.2.1&w=200&q=80",
        alt_text: "here is your utilization"
      },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: "Your user id is: " + u_id
        }
      },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text:
            "To view this report online, please <https://prod-useast-b.online.tableau.com/#/site/tessellationhq/views/ProjectReporting/BillableUtilization|click here>."
        }
      }
    ]
  };

  const args = {
    token: process.env.SLACK_BOT_TOKEN,
    trigger_id: trigger_id,
    view: JSON.stringify(modal)
  };

  const result = await axios.post(`${apiUrl}/views.open`, qs.stringify(args));

  //console.log(result.data);
};

module.exports = { displayHome, /*openModal*/ };
