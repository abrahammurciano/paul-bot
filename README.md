# Paul - The bestest polling bot ever

Hi! I'm Paul; a teeny tiny bot who's good at one thing. Making polls. And when I say good, I mean really really good. Like the bestest best bot ever at making polls. I can make open polls, I can make closed polls, I can make dynamically editable polls, and I can make them any size. And all that with a simple, good-looking, and easy to use interface! So come on and try me out in your server!

## Links

### [Invite Me](https://discord.com/api/oauth2/authorize?client_id=902944827598049321&permissions=2147551296&scope=bot%20applications.commands)

### [top.gg](https://top.gg/bot/902944827598049321)

### [GitHub](https://github.com/abrahammurciano/paul-bot)

### [Discord Server](https://discord.com/invite/mzhSRnnY78)

## Features

Paul has many features. In fact I believe it has the most features out of any other poll bot I could find. After all, that's why I made him; because I couldn't find a feature rich poll bot with an easy and well designed interface.

-   Uses a slash command to create the poll.
-   Uses buttons to vote and interact with existing polls.
-   Polls are persistent (That means if the bot goes offline it will remember its old polls when it comes back online)
-   Highly customizable permissions for each action (voting, editing, viewing).
-   Set expiry dates on polls.
-   Option to allow multiple votes per person.
-   Option to allow certain people (or everyone) to view the votes.
-   Option to allow people to add options to the poll.
-   Option to restrict votes to certain roles and/or users.
-   Beautiful interface.
-   Button for the poll creator to close the poll at will.

## Usage

This bot has a very simple interface. There is only one command. `/poll`. Below are the parameters it accepts.

### question

Specify the question that the poll is asking. This parameter is required.

> Example:
>
> `/poll question: Do you like potatoes?`
>
> ![question example](images/examples/question.png)

### options

Choose which options will be available for people to vote for. This parameter is optional, and by default will be Yes/No.

When entering options, you must separate each option with a pipe character (`|`). (Trailing spaces around the pipe will be ignored.)

> Example:
>
> `/poll question: How do you like your potatoes? options: boiled | mashed | in a stew`
>
> ![options example](images/examples/options.png)

### expires

With this parameter, you can choose when the poll will expire. Once the poll is expired, the vote buttons will disappear. By default, polls never expire.

When entering the expiry date/time, you may be quite liberal in its format. You can enter a relative date/time, such as "in 2 minutes", "1h20m", "tomorrow", "next week", etc; or you can enter an absolute date/time, such as "5 PM", "26 oct 2022", etc.

When using an absolute time such as "5 PM", it will be treated as UTC time. To specify a time zone, just include it in your input, for example "5 PM GMT+3" or "5 PM EST"

> Example:
>
> `/poll question: Do you like potatoes? expires: 1h20m`
>
> ![expires example](images/examples/expires.png)

### allow_multiple_votes

With this parameter you can control whether or not to allow people to vote on several different options. By default each voter may vote for only one option. If you set this to True, then each voter can vote for each option up to one time.

> Example:
>
> `/poll question: Do you like potatoes? allow_multiple_votes: True`
>
> ![allow_multiple_votes example](images/examples/allow_multiple_votes.png)

### allowed_vote_viewers

This parameter allows you to specify which users or roles are allowed to see who voted for each option. By default, votes are private and cannot be seen by anyone.

When specifying this parameter, you must mention all the roles and/or users you want to allow.

If this parameter is specified, then an additional button will appear underneath the poll which can be clicked by the allowed people for them to see the votes.

> Example:
>
> `/poll question: Do you like potatoes? allowed_vote_viewers: @everyone`
>
> ![allowed_vote_viewers example](images/examples/allowed_vote_viewers.png)

### allowed_editors

With this parameter, you can specify who will be allowed to add options to the poll. By default, only you can add options.

People with permission may click the "Add Option" button, after which the bot will prompt them to enter a new option within a minute. When they do, the option will be added to the poll with a note saying who it was added by.

> Example:
>
> \*_Click "Add Option" button_
>
> ![allowed_editors example](images/examples/allowed_editors.png)

### allowed_voters

Use this parameter to restrict who may vote to a set of users and roles. By default everyone may vote.

> Example:
>
> `/poll question: Do you like potatoes? allowed_voters: @Admin|🔱 @Abraham|👑🔱`
>
> ![allowed_voters example](images/examples/allowed_voters.png)

### Closing the poll

You can use the big red button to close the poll manually without waiting for it to expire. Once you do this, there's no turning back. Only the poll creator can do this.
