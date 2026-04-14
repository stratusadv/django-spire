import { tool } from "@opencode-ai/plugin"
import path from "path"
import { $ } from "bun"

export default tool({
  description: "Run Django tests for a specific app",
  args: {
    app_path: tool.schema.string().describe("Django app path to test (e.g., 'app.explorer', 'mort.podcast')"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, ".opencode/tools/test-app.py")

    try {
      const result = await $`python ${script} ${args.app_path}`.cwd(context.worktree).text()
      return result.trim()
    } catch (error: any) {
      const stderr = error.stderr ? error.stderr.toString() : error.message
      return `Python execution failed:\n${stderr}`
    }
  },
})
