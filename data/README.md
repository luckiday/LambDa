## Benchmark Testing

### Benchmark project: bmw27
- Default settings
  - Rendering engine: cycles
  - Resolution: 1920x1080, 50%
  - Sampling: 1225

- Customized settings for testing the performance of multiple devices
  - Frame number: 1-6
  - Each frame contains a different camera position

To render the frames:
```bash
blender -b bmw27_cpu_282a.blend -o ./output/frame_#### -f 1 
```
- `-f 1`: Render the 1st frame.
- `--cycles-print-stats`: Show detailed statistics about memory and time usage.


### Related links
- Scores of other devices: https://www.cgdirector.com/blender-benchmark-results-updated-scores/
- Command line rendering: https://docs.blender.org/manual/en/latest/advanced/command_line/render.html

