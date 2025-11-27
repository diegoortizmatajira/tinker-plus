# Tinker-Plus

Tinker-Plus is a robust tool tailored for advanced PC gamers seeking greater
control and optimization of their gaming setups on Steam. It offers seamless
integration and powerful features to enhance customization, resolve
compatibility issues, and fine-tune runtime configurations for a smoother
gaming experience.

## Key Features

Tinker-Plus comes with versatile functionality, including:

- **Steam Integration:** Optimize settings and configurations for specific
  Steam games.
- **Proton Customization:** Enable or disable features like WineD3D, DXVK, and
  others for better compatibility.
- **Winetricks Support:** Easily manage game-specific requirements with
  Winetricks.
- **Dynamic Folder Linking:** Organize and manage game data efficiently.
- **SDL Configuration:** Adjust video drivers and SDL environment variables for
  improved performance.
- **External Tools:**
  - **GameMode:** Boost performance with system-level tuning.
  - **GameScope:** Enhance your gaming interface for immersive experiences.
- **Steam Utilities:** Utilize wrapper commands, Sniper, and Reaper tools for
  advanced game management.
- **Environment Optimization:** Enhance compatibility by adjusting runtime
  environments dynamically.

## Why Choose Tinker-Plus?

For gamers and power users who demand full control over their gaming
environment, Tinker-Plus simplifies complex configuration tasks. It empowers
users to fine-tune and micromanage their setups with ease, ensuring an
optimized experience for Steam gaming.

## Installation

1. Clone the repository or download the binaries.
2. Run the installation script:

```bash
# For Linux:
chmod +x ./tinker-plus.sh
./tinker-plus.sh install
```

Once installed, the `tplus` command is available globally for your user.

## Usage

Tinker-Plus integrates seamlessly with Steam as a Command Modifier or
Compatibility Tool.

## Configuration properties

[See the reference](./configuration_reference.md)

### Running with Modifications

To apply game-specific settings, use the following command for each game:

```bash
tplus run %command%
```

### Feature Customization

Tinker-Plus offers flexible configurations to match your gaming requirements:

- Fine-tune Proton settings for particular games.
- Link user or public folders dynamically for better data management.
- Use Winetricks for tailored game setup adjustments.
- Leverage GameScope or GameMode for enhanced system performance and graphics.

## Contributing

We welcome contributions! Fork the repository and submit your issues or pull
requests to help improve Tinker-Plus.

## License

Tinker-Plus is distributed under the MIT License.
