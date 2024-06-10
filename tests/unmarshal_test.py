import unittest
from tasman.unmarshal import unmarshal_device

TEST_XML_OK='<?xml version="1.0"?><networks><network id="1" name="tasman" description="test" active="true" quality_assessed="false" uid="837"><features><feature id="53010" name="testname" description="testdesc" active="false" data_provider="ICT" lat="-42.93" lng="147.62" quality_assessed="false" uid="208072008"><sensors><sensor id="8" name="testname" description="testdesc" depth="0.0" active="true" model="testmodel" min_threshold="" max_threshold="" quality_assessed="false" phenomenon_id="48" phenomenon_name="Voltage" phenomenon_uom="mV" uid="208130659"><observations><observation id="211934233" time="20111117T010856" value="3800.0"/></observations></sensor></sensors></feature></features></network></networks>'

TEST_XML_BAD='<?xml version="1.0"?><networks><network id="1" name="tasman" description="test" active="true" quality_assessed="false" uid="837"><features><feature id="53010" description="testdesc" active="false" data_provider="ICT" lat="-42.93" lng="147.62" quality_assessed="false" uid="208072008"><sensors><sensor id="8" name="testname" description="testdesc" depth="0.0" active="true" model="testmodel" min_threshold="" max_threshold="" quality_assessed="false" phenomenon_id="48" phenomenon_name="Voltage" phenomenon_uom="mV" uid="208130659"><observations><observation id="211934233" time="20111117T010856" value="3800.0"/></observations></sensor></sensors></feature></features></network></networks>'

class TestUnmarshal(unittest.TestCase):

    def test_unmarshal_device(self):
        dev = unmarshal_device(TEST_XML_OK.encode())
        self.assertEqual(dev.name, 'testname')
        self.assertEqual(dev.description, 'testdesc')
        self.assertEqual(dev.id, 53010)
        self.assertTrue(len(dev.sensors) == 1)
        self.assertTrue(len(dev.sensors[0].observations) == 1)
        
    def test_unmarshal_device_bad(self):
        with self.assertRaises(Exception) as context:
            unmarshal_device(TEST_XML_BAD.encode())
        self.assertTrue('name not found' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
