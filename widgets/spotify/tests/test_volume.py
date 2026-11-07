import importlib.machinery,importlib.util,json,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
p=Path(__file__).resolve().parents[1]/'contents/code/volume-spotify'
loader=importlib.machinery.SourceFileLoader('volume_spotify',str(p));spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m)
def stream(index,binary,name=''):
 return {'index':index,'properties':{'application.process.binary':binary,'application.name':name},'volume':{'front-left':{'value_percent':'65%'},'front-right':{'value_percent':'65%'}}}
class VolumeTests(unittest.TestCase):
 def test_selects_only_spotify(self):
  data=[stream(1,'spotify'),stream(2,'firefox','Firefox'),stream(3,'chromium','Chromium'),stream(4,'/usr/share/spotify/spotify')]
  with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps(data))):self.assertEqual([s['index'] for s in m.streams()],[1,4])
 def test_set_never_changes_global_or_other_apps(self):
  with patch.object(m,'streams',return_value=[stream(7,'spotify')]),patch.object(m.sys,'argv',['volume-spotify','definir','42']),patch.object(m.subprocess,'run') as run,patch('builtins.print'):
   m.main();self.assertEqual(run.call_args.args[0],['pactl','set-sink-input-volume','7','42%'])
 def test_invalid_level_changes_nothing(self):
  with patch.object(m.sys,'argv',['volume-spotify','definir','101']),patch.object(m.subprocess,'run') as run:
   with self.assertRaises(ValueError):m.main()
   run.assert_not_called()
if __name__=='__main__':unittest.main()
