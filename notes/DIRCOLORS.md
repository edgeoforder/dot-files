# dircolors

## Commands

To generate the standard  `.dircolors` file, run the following command:
```
dircolors > ~/.dircolors
```

To display the effect of `LS_COLORS`, run the following command:
```bash
echo "$LS_COLORS" | tr ':' '\n' | sed 's/\([^=]\+\)=\(.*\)/\x1B[\2m\1\x1B[0m/'
```

## Code Reference

### Effects

| Code | Description |
| --- | --- |
| 00 | Default |
| 01 | Bold |
| 04 | Underlined |
| 05 | Flashing |
| 07 | Reversed |
| 08 | Concealed |
