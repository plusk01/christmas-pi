#include <alsa/pcm.h>

int main() {
  int val;

  printf("ALSA library version: %s\n", SND_LIB_VERSION_STR);

  printf("\nPCM stream types:\n");
  for (val = 0; val <= SND_PCM_STREAM_LAST; val++)
    printf("  %s\n",
      snd_pcm_stream_name((snd_pcm_stream_t)val));

  return 0;
}