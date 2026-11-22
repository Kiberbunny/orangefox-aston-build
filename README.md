# OrangeFox (community) build attempt for OnePlus 12R / Ace 3

Попытка собрать комьюнити OrangeFox recovery для OnePlus 12R / Ace 3
(`astonc`, SM8550/kalama) через GitHub Actions, «как есть», без приватных
ассетов.

- Манифест: https://gitlab.com/OrangeFox/sync.git (ветка `16.0`)
- Дерево: https://github.com/rkbkosp/android_device_oneplus_astonc_OrangeFox
  (`fox_16.0`)
- Цель: `mka recoveryimage` → `out/target/product/astonc/recovery.img`

> ⚠️ Дерево автора рассчитано на наличие приватных импортов (OEM-образы,
> ключи, hardware/crypto зависимости). Данная сборка их НЕ содержит и идёт с
> `ALLOW_MISSING_DEPENDENCIES=true` — результат может быть нерабочим или
> не собраться вовсе. Прошивка на свой риск.

## Запуск
`Actions → Build OrangeFox (community) for astonc → Run workflow`

Артефакт: `orangefox-astonc-run-*` (`recovery.img`).

## Если не хватит ресурсов стандартного runner'а
- Перейти на Cirrus CI (бесплатно, 8 CPU/20GB): форк `OrangeFox-CI`, правка
  `config.sh`, запуск через cirrus-ci.com.
- Либо self-hosted x86_64 VPS.

<!-- bump -->
