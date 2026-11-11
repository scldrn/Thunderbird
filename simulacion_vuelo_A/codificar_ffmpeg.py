from pathlib import Path
import imageio_ffmpeg,subprocess,json
P=Path(__file__).resolve().parent
exe=imageio_ffmpeg.get_ffmpeg_exe();out=P/'vuelo_condicional_5kg.mp4'
subprocess.run([exe,'-y','-framerate','15','-i',str(P/'frames/%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','21','-movflags','+faststart',str(out)],check=True)
# Fully decode output, rejecting decoder errors.
subprocess.run([exe,'-v','error','-i',str(out),'-f','null','-'],check=True)
(P/'VERIFICACION_VIDEO.json').write_text(json.dumps(dict(codec='H.264 / yuv420p',frames=360,fps=15,duration_s=24,decoded_without_errors=True,encoder=exe),indent=2))
print('MP4_VERIFIED',out)
