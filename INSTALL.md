# Installation Manual

## Install Base System

Erase all content of <hdd-id> and replace it with random data.
```bash
dd if=/dev/zero bs=16M | openssl enc -aes-256-ctr -pass pass:x -nosalt | dd of=/dev/<hdd-id> bs=16M status=progress oflag=direct
```

Create partition table using `gdisk /dev/<hdd-id>`:
* boot partition, 2GiB, type `EF02`
* swap parition, 8GiB, type `8200`
* root partition, remaining space, type `8300`

Format partitions and create encrypted root partition:
```bash
mkfs.fat -F 32 /dev/<hdd-id-partition1>
mkswap /dev/<hdd-id-partition2>
swapon /dev/<hdd-id/partition2>
cryptsetup luksFormat /dev/<hdd-id-partion3>
cryptsetup luksOpen /dev/<hdd-id-partion3> cryptroot
mkfs.btrfs -L root /dev/mapper/cryptroot
mount /dev/mapper/cryptroot /mnt
btrfs subvolume create /mnt/@
btrfs subvolume create /mnt/@home
umount /mnt
```

Mount the partitions:
```bash
mount -o noatime,compress=zstd:3,space_cache=v2,commit=120,discard=async,subvol=@ /dev/mapper/cryptroot /mnt
mkdir -p /mnt/{boot,home}
mount -o noatime,compress=zstd:3,space_cache=v2,commit=120,discard=async,subvol=@home /dev/mapper/cryptroot /mnt/home
mount /dev/<hdd-id-partion1> /mnt/boot
```

Connect to the internet.

Update hardware clock to use accurate UTC:
```bash
timedatectl
timedatectl set-ntp true
timedatectl set-local-rtc 0 --adjust-system-clock
hwclock --systohc --utc
timedatectl
```

Install base system:
```bash
pacstrap -K /mnt base base-devel linux linux-firmware btrfs-progs <intel|amd>-ucode iwd dhcpcd openssh bluez bluez-utils vim git
```

Generate the `fstab` file:
```bash
genfstab -U /mnt >> /mnt/etc/fstab
```

Change root to the new system:
```bash
arch-chroot /mnt
```

Set the time zone of the new system:
```bash
ln -sf /usr/share/zoneinfo/<time zone> /etc/localtime
timedatectl set-ntp true
hwclock --systohc
```

Set the locale, e.g. for English and German:
```bash
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
echo "de_DE.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf
echo "KEYMAP=us" > /etc/vconsole.conf
echo "XKBLAYOUT=us" >> /etc/vconsole.conf
echo "XKBMODEL=us-intl" >> /etc/vconsole.conf
echo "FONT=LatGrkCyr-12x22" >> /etc/vconsole.conf
```

Set the host name, e.g. `arch`:
```bash
echo "arch" > /etc/hostname
echo "127.0.0.1 localhost" > /etc/hosts
echo "::1       localhost" >> /etc/hosts
echo "127.0.1.1 arch.localdomain arch" >> /etc/hosts
```

Set root password:
```bash
passwd
```

Install the boot loader:
```bash
bootctl --path=/boot install
echo "default arch" > /boot/loader/loader.conf
echo "timeout 0" >> /boot/loader/loader.conf
```

Initialize the pacman keyring:
```bash
pacman-key --init
pacman-key --populate
```

Enable base service:
```bash
systemctl enable systemd-boot-update.service
systemctl enable systemd-timesyncd.service
systemctl enable systemd-resolved.service
systemctl enable iwd.service
systemctl enable dhcpcd.service
```

Create a user, add them to the `wheel` group to allow `sudo` usage and set their password:
```bash
useradd -m -G wheel -s /bin/bash <user>
passwd <user>
```

Enable members of the `wheel` group to use `sudo`:
```bash
sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers
```

Configure and regenerate the boot image by adding `btrfs` to the module and `encrypt` (before `filesystem`) in the hook section of `/etc/mkinitcpio.conf` then run:
```bash
mkinitcpio -P
```

Create bootloader entry:
```bash
blkid > /boot/loader/entries/arch.conf
echo "title Arch Linux" >> /boot/loader/entries/arch.conf
echo "linux /vmlinuz-linux" >> /boot/loader/entries/arch.conf
echo "initrd /intel-ucode.img" >> /boot/loader/entries/arch.conf
echo "initrd /initramfs-linux.img" >> /boot/loader/entries/arch.conf
echo "options rd.luks.uuid=<uuid of hdd-id-partition-3> rd.luks.name=<uuid of hdd-id-partition-3>=cryptroot root=/dev/mapper/cryptroot rootflags=subvol=@ rw" >> /boot/loader/entries/arch.conf
```

Restart the new system.

## Initial Configurations

Configure DNS by editing `/etc/systemd/resolved.conf`:
```bash
[Resolve]
DNS=<primary dns> 
FallbackDNS=<fallback dns>
Domains=~.
DNSSEC=no
MulticastDNS=yes
LMNR=no
```

Install AUR helper `yay`:
```bash
git clone https://aur.archlinux.org/yay-bin.git
cd yay-bin
makepkg -si
```

## Graphical Desktop Enviroment Configuration

Install window manager, terminal emulator and browser (choose `pipewire-jack` as audio provider):
```bash
yay -S xorg-server xorg-xinit autorandr arandr qtile kitty qutebrowser
```
