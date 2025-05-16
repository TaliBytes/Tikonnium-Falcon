# Tikonium Falcon Project

## Background

My parents use one of those little robot vacuums to keep their kitchen clean from everyday use. Their old one, a Tikom branded robot, recently began suffering from thinking it was stuck when, in reality, it was in the middle of the open floor. Because it could get "stuck" on nothing, my parents purchased a new vacuum bot. At the same time, Sam Meech-Ward published ["You Should Hack Your Roomba"](https://youtu.be/mTpkV7xZln0) on YouTube.

Tiko, as the bot was affectionately named by my 3 year old, was slated for disposal. So, in light of the pending disposal, the inspiration from Mr Meech-Ward, and the adoration from my 3-year old (and let's be real, myself and the rest of my family too)... I had but one obvious choice: to gut the poor vacuum, provide updated electronics (except the existing wheel motors), and turn it into a (non-vacuuming) Millennium Falcon from Star Wars. Hence the name, "Tikonnium Falcon."

## Goals

There are a few specific goals I am looking to achieve with this project. The Tikonnium:

- Needs to be controlled remotely via a phone (via a web app instead of a native app)
- Ideally, I'd like to integrate a camera to give it an on-screen first-person view (FPV)

I also want to achieve the following personal goals:

- Learn the basics of Micro Controllers (via Micro-Python)
- Learn the basics of electronics hardware/prototyping (eg breadboarding, etc)

## Additional Notes

This project uses an 128x64 I2C display which runs with SSD1306 drivers; Tiko uses the [Adafruit SSD1306 micropython library](https://github.com/adafruit/micropython-adafruit-ssd1306/tree/master) to interface with the display.

## PROJECT STATUS

The project is currently considered complete, though more could be done if ever I choose to pick it back up.

*The circuit-diagram.png was created using [Circuit Diagram Web Editor.](https://circuit-diagram.org/)*
