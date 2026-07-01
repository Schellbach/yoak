import { useState, useEffect } from "react";
import { Save } from "lucide-react";
import { getConfig, getModelOptions, setConfig } from "@/api/client";

export default function SettingsPage() {
  const [config, setLocalConfig] = useState<any>(null);
  const [modelOptions, setModelOptions] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getConfig().then((res) => setLocalConfig(res.config));
    getModelOptions().then((res) => {
      const cloud = res.cloud_providers.flatMap((p) => p.models);
      setModelOptions([...cloud, ...res.local.models.map((m) => `ollama/${m}`)]);
    });
  }, []);

  const handleSave = async (key: string, value: any) => {
    setSaving(true);
    try {
      await setConfig(key, value);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  if (!config) return <div className="p-6 text-gray-500">Loading...</div>;

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <header className="border-b border-gray-800 px-6 py-3">
        <h1 className="text-lg font-semibold">Settings</h1>
      </header>

      <div className="p-6 space-y-6 max-w-2xl">
        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-gray-400">Model Configuration</h2>

          <div>
            <label className="block text-xs text-gray-500 mb-1">Model</label>
            <input
              list="yoak-models"
              defaultValue={config.model?.model}
              onBlur={(e) => handleSave("model.model", e.target.value)}
              className="input w-full"
            />
            <datalist id="yoak-models">
              {modelOptions.map((m) => (
                <option key={m} value={m} />
              ))}
            </datalist>
            <p className="text-xs text-gray-600 mt-1">
              Cloud: deepseek/deepseek-chat, zhipuai/glm-4-flash, gpt-4o, anthropic/claude-sonnet-4-20250514
            </p>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">Temperature</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="2"
              defaultValue={config.model?.temperature}
              onBlur={(e) => handleSave("model.temperature", parseFloat(e.target.value))}
              className="input w-32"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">Max Tokens</label>
            <input
              type="number"
              step="256"
              min="256"
              defaultValue={config.model?.max_tokens}
              onBlur={(e) => handleSave("model.max_tokens", parseInt(e.target.value))}
              className="input w-32"
            />
          </div>
        </div>

        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-gray-400">Ollama (Local Models)</h2>

          <div className="flex items-center gap-3">
            <label className="text-xs text-gray-500">Enabled</label>
            <button
              onClick={() => handleSave("ollama.enabled", !config.ollama?.enabled)}
              className={`relative h-6 w-11 rounded-full transition ${
                config.ollama?.enabled ? "bg-yoak-600" : "bg-gray-700"
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white transition ${
                  config.ollama?.enabled ? "translate-x-5" : ""
                }`}
              />
            </button>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">Base URL</label>
            <input
              defaultValue={config.ollama?.base_url}
              onBlur={(e) => handleSave("ollama.base_url", e.target.value)}
              className="input w-full"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">Model</label>
            <input
              list="yoak-ollama-models"
              defaultValue={config.ollama?.model}
              onBlur={(e) => handleSave("ollama.model", e.target.value)}
              className="input w-full"
            />
            <datalist id="yoak-ollama-models">
              {modelOptions
                .filter((m) => m.startsWith("ollama/"))
                .map((m) => m.replace("ollama/", ""))
                .map((m) => (
                  <option key={m} value={m} />
                ))}
            </datalist>
          </div>
        </div>

        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-gray-400">Project</h2>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Project Name</label>
            <input
              defaultValue={config.project_name}
              onBlur={(e) => handleSave("project_name", e.target.value)}
              className="input w-full"
            />
          </div>
        </div>

        {saved && (
          <div className="flex items-center gap-2 text-sm text-green-400">
            <Save size={14} /> Settings saved
          </div>
        )}
      </div>
    </div>
  );
}
