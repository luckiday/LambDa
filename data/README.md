## Benchmark Testing

**Benchmark project: bmw27**
- Default settings
  - Rendering engine: cycles
  - Resolution: 1920x1080, 50%
  - Sampling: 1225

- Customized settings for testing the performance of multiple devices
  - Frame number: 1-6
  - Each frame contains a different camera position

To render the frames:
```bash
blender -b bmw27_cpu.blend -o ./output/frame_#### -f 1 
```
Show detailed statistics about memory and time usage: `--cycles-print-stats`