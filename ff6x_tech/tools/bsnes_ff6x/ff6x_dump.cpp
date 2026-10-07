// FF6X test harness hooks (not part of bsnes): raw access to WRAM / VRAM / CGRAM / OAM.
#define private public
#define protected public
#include <sfc/sfc.hpp>
#undef private
#undef protected
#include <stdint.h>

extern "C" __attribute__((visibility("default"))) void *retro_ff6x_wram() { return SuperFamicom::cpu.wram; }

extern "C" __attribute__((visibility("default"))) int retro_ff6x_fastppu() { return SuperFamicom::system.fastPPU() ? 1 : 0; }

/* 0 = VRAM (64 KiB), 1 = CGRAM (512 B), 2 = OAM (544 B; accurate PPU only) */
extern "C" __attribute__((visibility("default"))) void retro_ff6x_dump(unsigned which, uint8_t *out)
{
	bool fast = SuperFamicom::system.fastPPU();
	if (which == 0) {
		for (unsigned i = 0; i < 32768; i++) {
			unsigned w = fast ? (unsigned)SuperFamicom::ppufast.vram[i] : (unsigned)SuperFamicom::ppu.vram.data[i];
			out[2 * i] = w & 0xff; out[2 * i + 1] = (w >> 8) & 0xff;
		}
	} else if (which == 1) {
		for (unsigned i = 0; i < 256; i++) {
			unsigned c = fast ? (unsigned)SuperFamicom::ppufast.cgram[i] : (unsigned)SuperFamicom::ppu.screen.cgram[i];
			out[2 * i] = c & 0xff; out[2 * i + 1] = (c >> 8) & 0xff;
		}
	} else if (which == 2 && !fast) {
		for (unsigned i = 0; i < 544; i++) out[i] = SuperFamicom::ppu.obj.oam.read(i);
	}
}

/* cartridge SRAM (battery RAM): pointer / size */
extern "C" __attribute__((visibility("default"))) void *retro_ff6x_sram() { return SuperFamicom::cartridge.ram.data(); }
extern "C" __attribute__((visibility("default"))) unsigned retro_ff6x_sram_size() { return SuperFamicom::cartridge.ram.size(); }
