## Task profile: mobile-app

Shape the rewritten prompt as a mobile platform implementation brief.

- Name the target platform (iOS, Android, or both), minimum OS version, and whether the
  approach is native, React Native, Flutter, or another cross-platform framework.
- Identify affected screens, navigation flow, and state management pattern already used
  in the project; do not introduce a new one without stating the tradeoff.
- Call out required permissions (camera, location, notifications, background execution)
  and require the least-privilege runtime request flow for each.
- Cover offline behavior, local caching, and sync-conflict resolution when the feature
  touches network state.
- Require handling of device fragmentation relevant to the change: screen sizes, notches
  and safe areas, dark mode, dynamic type or font scaling, and low-memory conditions.
- For anything touching store submission, name the applicable App Store or Play Store
  guideline the change must satisfy (privacy manifest, data-safety form, background
  execution limits, deep link verification).
- Make push notification payload shape, delivery guarantees, and opt-in flow explicit
  when notifications are involved.
- Acceptance should include the closest platform tests, a device or simulator run,
  behavior under airplane mode when offline logic is touched, and confirmation the change
  does not violate store review guidelines.
