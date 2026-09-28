import { ref } from 'vue'

export function useCameraChannels() {
  const channels = ref([
    {
      id: 'cam-01',
      name: 'Lane 1 - Toll Plaza (Valid Pass)',
      type: 'scenario',
      filename: 'scenario_1_valid.mp4',
      location: 'NH-48 Toll Plaza Booth 01',
      status: 'ONLINE'
    },
    {
      id: 'cam-02',
      name: 'Lane 2 - Express (Type Mismatch)',
      type: 'scenario',
      filename: 'scenario_2_type_mismatch.mp4',
      location: 'NH-48 Toll Plaza Booth 02',
      status: 'ONLINE'
    },
    {
      id: 'cam-03',
      name: 'Lane 3 - Heavy Freight (Color Mismatch)',
      type: 'scenario',
      filename: 'scenario_3_color_mismatch.mp4',
      location: 'NH-48 Freight Inspection Bay',
      status: 'ONLINE'
    },
    {
      id: 'cam-04',
      name: 'Night Vision IR - KM 42 Junction',
      type: 'scenario',
      filename: 'scenario_4_unregistered.mp4',
      location: 'NH-48 Night Highway KM 42',
      status: 'ONLINE'
    },
    {
      id: 'webcam-01',
      name: 'Local USB / Field Checkpoint Camera',
      type: 'webcam',
      filename: '',
      location: 'Mobile Patrol Unit 04',
      status: 'STANDBY'
    }
  ])

  const selectedChannelId = ref('cam-01')

  const getSelectedChannel = () => {
    return channels.value.find(c => c.id === selectedChannelId.value) || channels.value[0]
  }

  const addRTSPChannel = (name, rtspUrl, location = 'Highway Checkpoint') => {
    const newId = `rtsp-${Date.now()}`
    channels.value.push({
      id: newId,
      name: name || `RTSP Stream (${newId.slice(-4)})`,
      type: 'rtsp',
      rtsp_url: rtspUrl,
      location: location,
      status: 'ONLINE'
    })
    selectedChannelId.value = newId
    return newId
  }

  return {
    channels,
    selectedChannelId,
    getSelectedChannel,
    addRTSPChannel
  }
}
