import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { api } from "../lib/api";

interface Activity {
  id: number;
  action: string;
  details?: string;
  created_at: string;
  actor_name?: string;
}

interface SettingsState {
  in_app_notifications: boolean;
  email_notifications: boolean;
  ai_analysis_notifications: boolean;
  critical_bug_alerts: boolean;
  sprint_deadline_alerts: boolean;
  auto_refresh_dashboard: boolean;
  compact_mode: boolean;
  two_factor_auth: boolean;
  session_timeout: number;
}

const defaultSettings: SettingsState = {
  in_app_notifications: true,
  email_notifications: false,
  ai_analysis_notifications: true,
  critical_bug_alerts: true,
  sprint_deadline_alerts: true,
  auto_refresh_dashboard: true,
  compact_mode: false,
  two_factor_auth: false,
  session_timeout: 30,
};

export default function SettingsPage() {
  const [settings, setSettings] =
    useState<SettingsState>(defaultSettings);

  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);

    try {
      try {
        const response = await api.get("/api/users/me/settings");

        setSettings({
          ...defaultSettings,
          ...response.data,
        });
      } catch {
        // Use default settings if the endpoint is unavailable.
      }

      try {
        const response = await api.get("/api/users/activity");

        const data = response.data;

        if (Array.isArray(data)) {
          setActivities(data);
        } else if (Array.isArray(data?.items)) {
          setActivities(data.items);
        } else {
          setActivities([]);
        }
      } catch {
        setActivities([]);
      }
    } finally {
      setLoading(false);
    }
  }

  async function saveSettings() {
    setSaving(true);
    setMessage("");

    try {
      await api.put("/api/users/me/settings", settings);

      setMessage("Settings saved successfully.");
    } catch {
      setMessage(
        "Settings could not be saved. Please try again."
      );
    } finally {
      setSaving(false);
    }
  }

  function updateSetting(
    key: keyof SettingsState,
    value: boolean | number
  ) {
    setSettings((previous) => ({
      ...previous,
      [key]: value,
    }));

    setMessage("");
  }

  if (loading) {
    return (
      <Layout title="Settings">
        <div className="flex min-h-[300px] items-center justify-center">
          <p className="text-muted-foreground">
            Loading Settings...
          </p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Settings">
      <div className="space-y-6">

        {/* Save message */}
        {message && (
          <div
            className={`rounded-xl border p-4 text-sm ${
              message.includes("successfully")
                ? "border-green-500/40 bg-green-500/10 text-green-300"
                : "border-red-500/40 bg-red-500/10 text-red-300"
            }`}
          >
            {message}
          </div>
        )}

        {/* Settings Cards */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">

          {/* Notification Settings */}
          <section className="rounded-2xl border border-border bg-card p-6">
            <h2 className="mb-5 text-xl font-semibold text-foreground">
              Notification Settings
            </h2>

            <div className="space-y-5">

              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-foreground">
                    In-App Notifications
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Show notifications inside BugFlow.
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={settings.in_app_notifications}
                  onChange={(event) =>
                    updateSetting(
                      "in_app_notifications",
                      event.target.checked
                    )
                  }
                  className="h-4 w-4"
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-foreground">
                    Email Notifications
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Receive important updates by email.
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={settings.email_notifications}
                  onChange={(event) =>
                    updateSetting(
                      "email_notifications",
                      event.target.checked
                    )
                  }
                  className="h-4 w-4"
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-foreground">
                    AI Analysis Notifications
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Get notified when AI analysis is completed.
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={settings.ai_analysis_notifications}
                  onChange={(event) =>
                    updateSetting(
                      "ai_analysis_notifications",
                      event.target.checked
                    )
                  }
                  className="h-4 w-4"
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-foreground">
                    Critical Bug Alerts
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Alert you when critical bugs are created.
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={settings.critical_bug_alerts}
                  onChange={(event) =>
                    updateSetting(
                      "critical_bug_alerts",
                      event.target.checked
                    )
                  }
                  className="h-4 w-4"
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-foreground">
                    Sprint Deadline Alerts
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Receive alerts about sprint deadlines.
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={settings.sprint_deadline_alerts}
                  onChange={(event) =>
                    updateSetting(
                      "sprint_deadline_alerts",
                      event.target.checked
                    )
                  }
                  className="h-4 w-4"
                />
              </label>

            </div>
          </section>

          {/* Preferences */}
          <section className="rounded-2xl border border-border bg-card p-6">
            <h2 className="mb-5 text-xl font-semibold text-foreground">
              Preferences
            </h2>

            <div className="space-y-5">

              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-foreground">
                    Auto Refresh Dashboard
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Automatically refresh dashboard information.
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={settings.auto_refresh_dashboard}
                  onChange={(event) =>
                    updateSetting(
                      "auto_refresh_dashboard",
                      event.target.checked
                    )
                  }
                  className="h-4 w-4"
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-foreground">
                    Compact Mode
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Use a more compact interface layout.
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={settings.compact_mode}
                  onChange={(event) =>
                    updateSetting(
                      "compact_mode",
                      event.target.checked
                    )
                  }
                  className="h-4 w-4"
                />
              </label>

            </div>
          </section>

          {/* Security */}
          <section className="rounded-2xl border border-border bg-card p-6">
            <h2 className="mb-5 text-xl font-semibold text-foreground">
              Security
            </h2>

            <div className="space-y-5">

              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-foreground">
                    Two-Factor Authentication
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Add an additional layer of account security.
                  </p>
                </div>

                <input
                  type="checkbox"
                  checked={settings.two_factor_auth}
                  onChange={(event) =>
                    updateSetting(
                      "two_factor_auth",
                      event.target.checked
                    )
                  }
                  className="h-4 w-4"
                />
              </label>

              <div>
                <label
                  htmlFor="session-timeout"
                  className="mb-2 block font-medium text-foreground"
                >
                  Session Timeout
                </label>

                <p className="mb-3 text-sm text-muted-foreground">
                  Set the session timeout in minutes.
                </p>

                <input
                  id="session-timeout"
                  type="number"
                  min={5}
                  max={180}
                  value={settings.session_timeout}
                  onChange={(event) =>
                    updateSetting(
                      "session_timeout",
                      Number(event.target.value)
                    )
                  }
                  className="w-full rounded-xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary"
                />
              </div>

            </div>
          </section>

        </div>

        {/* Activity History */}
        <section className="rounded-2xl border border-border bg-card p-6">
          <h2 className="mb-5 text-xl font-semibold text-foreground">
            Activity History
          </h2>

          {activities.length === 0 ? (
            <div className="rounded-xl border border-border bg-background p-5">
              <p className="text-sm text-muted-foreground">
                No recent activity found.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className="rounded-xl border border-border bg-background p-4"
                >
                  <div className="flex flex-col gap-1">
                    <p className="font-medium text-foreground">
                      {activity.action}
                    </p>

                    {activity.details && (
                      <p className="text-sm text-muted-foreground">
                        {activity.details}
                      </p>
                    )}

                    <p className="text-xs text-muted-foreground">
                      {activity.actor_name
                        ? `${activity.actor_name} • `
                        : ""}
                      {new Date(
                        activity.created_at
                      ).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Save */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={saveSettings}
            disabled={saving}
            className="rounded-2xl bg-primary px-8 py-3 font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </div>

      </div>
    </Layout>
  );
}