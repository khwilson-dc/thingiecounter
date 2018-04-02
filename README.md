# thingiecounter

This counts thingies


## Installing

After changing the configuration in `local_settings.py`, run this on the Raspberry Pi:

```
cd pi
sudo bash install-Rpi.sh
```

Installing
```
virtualenv --no-site-packages -p python3 virt
source virt/bin/activate
pip install -r requirements.txt
python ./create_app_db.py
```
