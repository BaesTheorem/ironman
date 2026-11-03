# Exercise Log

A native iPhone copy of a paper training log plus a Couch to 5K quest. The log: one page per week, three
training days, reps per set, a weekly set target and a rest interval per
exercise. Logging a set starts the rest timer, and the timer fires a
notification so it works with the phone locked.

The whole log is one JSON file. Pick a folder in iCloud Drive or Google Drive
once and the app keeps `exercise-log.json` there, which puts the same file on
the Mac for scripts to read. `bin/ironman` is that reader.

## The sheet it copies

| Exercise | Sets / week | Rest |
|---|---|---|
| Horizontal Push, Vertical Push, Squats, Calves | 10 | 3 min (calves 1 min) |
| Vertical Pull, Horizontal Pull | 5 | 3 min |
| Bicep Curls, Lower Abs, Upper Abs, Obliques, Tricep Extension, Side Delt Raises, Rear Delt Raises | 5 | 1 min |

The "Progression" column is free text (load or variant, "100kg chest press")
and is snapshotted into each week, so the history shows what you were lifting
then. Progression is double progression: each exercise has a rep range
(10 to 15 for the compounds, 12 to 15 for isolation work by default). When
three sets in one session reach the ceiling, the row shows "Hit 3×15.
Progress?" and offers the next step: the next rung of an optional ladder of
harder forms, or the current load plus a step (2.5 by default, parsed from a
leading number). Pick a load that puts the first set back near the floor. A checkbox per exercise per day is the paper strikethrough: done for
today, remaining boxes crossed out. Everything on the sheet is editable in
the app (list icon, top left).

## Look

The whole app is skinned after Old School RuneScape: stone panels with
bevelled edges, parchment dialogs, the RuneScape bitmap font with its
one-pixel shadow, yellow labels and orange headers. Exercises are skill
panels with the wiki's skill icons (push and arm work under Strength,
pulls under Attack, legs under Agility, trunk under Hitpoints), the weekly
tally is an XP bar, set boxes are inventory slots, and hitting three sets
at the ceiling raises the level-up dialog with the Strength jingle. The
Agility skill (Couch to 5K) uses the same skin.

**Music.** The Player tab has the game's music tab: 18 OSRS tracks
(Scape Main, Sea Shanty 2, Harmony, Newbie Melody, Adventure and friends)
bundled as AAC, playing through the list or looping one, with lock-screen
controls and playback that survives the screen locking. Star a track to
make it the default: the app opens on it and, with "Play on launch" set,
starts it. "Fanfare" plays on
a completed quest session.

**Character design.** Player > Character design is the Tutorial Island
screen: body type, head, jaw, torso, arms, hands, legs, feet, and colours
for hair, torso, legs, feet and skin, drawn as a 20 x 32 pixel figure with
the low-poly shading. The choice is stored under `avatar` in the JSON.

Third-party assets, all for personal use:

- Fonts `runescape.ttf`, `runescape_bold.ttf`, `runescape_small.ttf` from
  [RuneLite](https://github.com/runelite/runelite) (BSD-2-Clause).
- Music tracks (`Resources/Music/*.m4a`), skill icons and the level-up
  jingles from the
  [OSRS Wiki](https://oldschool.runescape.wiki) (CC BY-NC-SA 3.0; the
  underlying art and audio are Jagex's).
- Stone and parchment tiles are generated noise, drawn here.

## Skills

Two tabs: Skills and Player. Every log lives under its skill; tap a
tile to open it. Six skills on the OSRS experience table (level L needs
floor(sum over x < L of floor(x + 300·2^(x/7)) / 4); level 2 is 83 xp,
level 99 is 13,034,431). XP is derived from the logs on every read and
never stored, so the phone and the Mac can both rewrite the file.

| Skill | XP from |
|---|---|
| Strength | The exercise log: 10 + reps per set, 100 per exercise per week whose target is met. |
| Agility | The running quest, as before. |
| Hitpoints | Starts at level 10 (1154 xp). Sleep-goal nights: 60 xp for night one, +20 per consecutive night, capped at 200; a miss resets the run, not the XP. Daily steps from Fitbit: 1 xp per 100 steps, and every step past 10,000 counts double (15,000 steps is 200 xp). Healthy meals 40 each (logged under Hitpoints or as a healthy Cooking dish). Plus a third of all Strength and Agility XP, the game's combat rule. |
| Firemaking | Candle or stove 10, fireplace 40, campfire 90, bonfire 135, no lighter 202, in the rain 304. |
| Crafting | Small thing 50, real project 200, ambitious 600, masterwork 1500. |
| Cooking | Simple 30, everyday 70, involved 120, exotic 210, feast 300. |

Sleep nights and steps come from Fitbit through the Google Health API v4 (the
Fitbit Web API shut down on 2026-10-30): `bin/hitpoints-verify` reads the last
14 nights and the daily step series against a 450-minute goal (`--goal`; Google
has no sleep-goal endpoint), and writes them
into `skills.nights` and `skills.steps` (nights over anything claimed in
the app; zero-step days skipped). The harness's quest watcher runs it every half hour.
A level gained on either side raises the level-up banner with that
skill's jingle the next time the app is in front.

Logs live under `skills` in the JSON:

```json
"skills": {
  "nights": [{"date": "2026-09-27", "minutes": 470, "goalMet": true, "verified": true}],
  "steps":  [{"date": "2026-09-27", "steps": 11240}],
  "meals":  [{"id": "…", "date": "2026-09-27", "note": "Lentil curry", "loggedAt": "…"}],
  "fires":  [{"id": "…", "date": "2026-09-26", "kind": "campfire", "note": "", "loggedAt": "…"}],
  "crafts": [{"id": "…", "date": "2026-09-25", "name": "Map", "tier": "ambitious", "note": "", "loggedAt": "…"}],
  "cooks":  [{"id": "…", "date": "2026-09-27", "dish": "Ramen", "tier": "exotic", "healthy": true, "note": "", "loggedAt": "…"}]
}
```

`bin/ironman skills` prints every level and XP.

## Build and install

```bash
cd ios
cp Config/Signing.xcconfig.example Config/Signing.xcconfig   # set your team
scripts/build.sh              # unsigned compile check
scripts/build.sh --device     # signed Release build
scripts/install.sh            # build, install, and launch on a paired iPhone
```

The Xcode project is generated by XcodeGen and gitignored. Anything set in
the Xcode GUI is wiped on the next `xcodegen generate`, so settings belong in
`project.yml` or `Config/Signing.xcconfig`.

Requirements: Xcode with the iOS platform installed
(`xcodebuild -downloadPlatform iOS` if a device build says the platform is
missing), `brew install xcodegen`, an Apple developer team.

## Sync

Settings > Choose sync folder, then pick any folder in Files: an "Exercise
Log" folder in iCloud Drive, or one inside Google Drive if the Drive app is
installed. No iCloud entitlement is involved; access comes from the folder
picker and is kept as a security-scoped bookmark. The provider does the
syncing.

The app's own Documents folder is also visible in Files
(`UIFileSharingEnabled`), so the file is reachable even with no folder chosen.

Reconciliation is by `updatedAt`: on every foreground the app reads the
cloud copy and adopts it if it is newer, otherwise pushes its own. Edits
push about two seconds after they happen. The phone is the only regular
writer; a script may edit the file while the app is closed and the edit is
picked up on the next launch.

## Reading it on the Mac

```bash
bin/ironman status            # file location, last update, this week's table
bin/ironman week 2026-09-20   # one week
bin/ironman weeks -n 12       # sets done vs target per week
bin/ironman markdown          # this week as a markdown table
bin/ironman vault             # one Obsidian note per logged week
bin/ironman skills            # levels and xp per skill
bin/ironman json              # the raw file
```

The file is found at `--file`, then `$EXERCISE_LOG_JSON`, then
`~/Library/Mobile Documents/com~apple~CloudDocs/Exercise Log/`, then
`~/My Drive/Exercise Log/`. `vault` writes to `$EXERCISE_LOG_VAULT_DIR` or
`~/Exobrain/Areas/Health & Fitness/Exercise Log/`, and only rewrites a note
whose content changed.

## JSON schema (v1)

```json
{
  "app": "exercise-log",
  "schemaVersion": 1,
  "updatedAt": "2026-09-24T05:10:00.000Z",
  "exercises": [
    {"id": "horizontal-push", "name": "Horizontal Push", "weeklySets": 10,
     "restSeconds": 180, "progression": "100kg chest press", "archived": false,
     "repMin": 10, "repMax": 15, "loadStep": 2.5,
     "ladder": ["incline pushups", "pushups", "chest press"]}
  ],
  "avatar": {"name": "Player", "female": false, "head": 1, "jaw": 0, "torso": 0,
             "arms": 0, "hands": 0, "legs": 0, "feet": 0, "hairColor": 0,
             "torsoColor": 1, "legsColor": 2, "feetColor": 0, "skinColor": 0},
  "weeks": [
    {
      "weekOf": "2026-09-20",
      "notes": "",
      "progressions": {"horizontal-push": "100kg chest press"},
      "progressedAt": {"horizontal-push": "2026-09-22T17:30:00.000Z"},
      "days": [
        {"day": 1, "date": "2026-09-22",
         "entries": {
           "horizontal-push": {"done": true,
             "sets": [{"reps": 12, "loggedAt": "2026-09-22T17:00:00.000Z", "note": ""}]}
         }},
        {"day": 2, "entries": {}},
        {"day": 3, "entries": {}}
      ]
    }
  ]
}
```

- `weekOf` is the first day of the calendar week in the phone's locale
  (Sunday in the US), `yyyy-MM-dd`.
- `day.date` is stamped the first time a set is logged that day, or set by
  long-pressing the day tab.
- `entries` is keyed by exercise id so readers join on it rather than on
  position. Ids are slugs of the name for the built-in rows.
- `weeklySets` is the target for the week, summed across the three days.
- `repMin`/`repMax` is the working range; `ladder` (optional) lists harder
  forms in order; `loadStep` is the suggested increase when the progression
  starts with a number. `progressedAt` records when the progression was
  advanced (or the prompt snoozed) that week, and sets logged before it do
  not count toward the next prompt.
- Timestamps are ISO 8601 in UTC. The reader accepts them with or without
  fractional seconds.

## The running quest

The Agility skill is Couch to 5K as a game: nine chapters of three sessions,
from eight 60-second jogs to thirty minutes continuous, each session
bracketed by a five-minute walk. Finishing sessions raises an Agility level
on the OSRS experience table; the full plan, verified, lands near level 50.
There are no streaks. The design pays for leaving the house: finishing the
warm-up earns 1000 xp, finishing the session 1500 more, and a Fitbit match
1500 more plus 50 per active minute. A run Fitbit saw that was never
started in the app still earns 500 plus active minutes.

The phone runs the intervals. Cues are spoken (`AVSpeechSynthesizer`) over
a looped silent track that keeps the audio session open in the background,
so they arrive with the screen locked, and every boundary also fires a local
notification. Fitbit's auto-detect is enough to verify a session; starting a
Run on the watch adds GPS distance and full active-minute credit.

The Mac verifies. `bin/quest-verify` pulls Fitbit exercises from the Google
Health API (token from the harness's `fitbit-mcp/bin/google-health-token`,
never refreshed here), converts them to the Fitbit activity shape (active
minutes come from heart-rate zone time), matches each attempt to
the activity that overlaps it most, and writes a `verification` block into
the attempt. Bikes never match. It is idempotent, so run it whenever. The
rules are in `lib/quest.py` and mirrored in
`ios/ExerciseLog/Sources/Model/Quest.swift`; change both or neither.
`tests/test_quest.py` covers them (`uv run --with pytest pytest`).

```bash
bin/ironman quest          # level, xp, next session, recent attempts
bin/ironman quest --line   # one line for a briefing
bin/quest-verify --dry-run      # what would match, written nowhere
```

In the JSON, `quest` holds `plan` (`c25k`), `startedAt`, and `sessions`:
each with `id`, `week` and `day` (absent on a free run), `startedAt`,
`endedAt`, `elapsedSeconds`, `jogSecondsDone`, `completed`, and optionally
`verification` (`logId`, `source`, `activityName`, `startTime`,
`durationSeconds`, `distanceKm`, `averageHeartRate`, `activeMinutes`,
`verifiedAt`). XP and level are computed from `sessions`, never stored.
