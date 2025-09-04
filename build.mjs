import * as esbuild from 'esbuild'


async function build(app_name) {
  const watch = process.argv.includes('--watch');
  const buildConfig = {
    outfile: 'django_spire/core/static/django_spire/js/core.js',
    entryPoints: ['django_spire/core/frontend/src/index.js'],
    write: true,
    bundle: true,
    platform: 'browser',
    format: 'iife', // This creates the classic, self-executing script format
    sourcemap: true,
    // esbuild can strip TypeScript types, so we don't need a separate step.
  };

  if (watch) {
    console.log('Watching for changes...');
    let ctx = await esbuild.context(buildConfig);
    await ctx.watch();
  } else {
    try {
      await esbuild.build(buildConfig);
      console.log('Build successful! Output file created at ' + outfilePath);
    } catch (err) {
      process.exit(1); // Exit with a non-zero code on build failure
    }
  }
}

await build();
