# Linux Aware Debugging


## Prerequisites

- APU successfully boots Linux
- Yocto build available for vmlinux and Kernel sources
- Trace32 GUIs started via `start_zukimo_session.sh` script


## Module debugging

First, attach both Trace32 GUIs to Alcatraz and Zukimo and load the Linux Awareness.

1. Run `alc_zephyr.cmm` script in the ARM-1 Trace32 window and click "go" to let the BL3 start the APU
2. Wait until the APU Linux booted up
3. Run `zuk_linux.cmm` script in the ARM-2 Trace32 window and click "go" to resume execution


### Debugging from the start

1. Click Linux → Module Debugging → Debug Module on init...
2. Enter the kernel module name (eg. `dct_i2c`) and click Ok (this dialog will remain open)
3. Trace32 now automatically sets a breakpoint at the `do_init_module()` kernel function, which will load the module
4. Insert the module via Linux shell (eg. `modprobe dct_i2c`)
5. Now a file open dialog appears. Open the `.ko` file (eg. `dct_i2c.ko`) from the Yocto Linux build folder to load the module symbols into the debugger
6. Trace32 will continue execution and stop in the module's startup


### Debugging a running module

For debugging an already loaded module, the module's debugger symbols must be loaded.

1. Enter in the Trace32 command line: `TASK.sYmbol.LOADMod "dct_i2c"`
2. A file open dialog appears to load the module's `.ko` file. Most likely, Trace32 will not find the associated source files for the module. Check the source paths: `sYmbol.List.SOURCE /ERRORS`


## Kernel debugging

The script `zuk_linux.cmm` assumes, that the MMU is already initialized. If it
is run before the MMU is initalized, access to kernel symbols is not possible
via virtual addresses and will lead to an error accessing the symbol
`__kpti_forced`.

If you want to debug the kernel from the start, do not initialize the debugger
MMU. Just remove all the lines starting from the line
```
PRINT "initializing debugger MMU..."
```
until the end of the script.

Then start U-Boot, but don't let it start the kernel yet.

Now execute the modified `zuk_linux.cmm` script, with the following lines commented-in:
```
go 0x80200000 /Onchip
wait !STATE.RUN()
```

This will set an onchip-breakpoint at the kernel entry address `0x80200000` and
resume execution. Trace32 will wait until that breakpoint is hit.


## Other Information

- Make sure that `SYStem.option.DUALPORT` is set to OFF
- Use `task.check` to check if Linux Awareness is working properly
- Use `TargetSystem` to see the state of all CPU cores


### Symbol addresses

All the symbol addresses in Linux are virtual addresses translated by the MMU
into physical addresses. The kernel and every process each have their own
address space. The T32 term for these address spaces is "MMUSPACE". Every
address space has a unique number, the kernel has `0`.

An address is expressed as `<access class>:<mmuspace>::<virtual address>`

For example the symbol `linux_banner` has address `NSD:0000::FFFFFFC008B65380`.
That means it is in the virtual address space of the kernel at virtual address
`0xFFFFFFC008B65380`. That memory will be accessed by the debugger with memory
access class `NSD`.

Trace32 will fetch the MMU configuration from Linux and translate the virtual
address into a physical address by itself. Using the `AXI` access class does
not work for virtual addresses, though; the reason is not yet known.


### Memory Access Classes

Every CPU architecture supports different access classes. The following are
taken from `pdf/debugger_armv8v9.pdf` in the T32 installation directory.

|Class|Description|
|---|---|
|A | Absolute addressing (physical address)|
|AXI| Memory access via AXI MEM-AP|
|D | Data memory|
|E|Run-time memory access|
|M|EL3 Mode (TrustZone devices)|
|H|EL2/Hypervisor Mode|
|N|EL0/1 Non-secure Mode (TrustZone devices)|
|P|Program memory|
|S|Supervisor Memory (priviledged access)|
|SPR|System Registers, Special Purpose Registers|
|X|AArch64 Arm64 Code|
|Z|Secure Mode (TrustZone devices)|
