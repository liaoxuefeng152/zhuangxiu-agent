import React, { useState, useMemo, useEffect } from 'react'
import { View, Text, ScrollView, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { safeSwitchTab, TAB_HOME } from '../../utils/navigation'
import './index.scss'

// P38 原型：热门城市仅 5 个（展示用短名，选中时存带「市」与列表一致）
const HOT_CITIES = [
  { label: '北京', value: '北京市' },
  { label: '上海', value: '上海市' },
  { label: '广州', value: '广州市' },
  { label: '深圳', value: '深圳市' },
  { label: '杭州', value: '杭州市' }
]
const PROVINCES: Record<string, string[]> = {
  广东: ['广州市', '深圳市', '东莞市', '佛山市', '珠海市', '惠州市', '中山市', '江门市', '湛江市', '茂名市', '肇庆市', '梅州市', '汕尾市', '河源市', '阳江市', '清远市', '潮州市', '揭阳市', '云浮市'],
  北京: ['北京市'],
  上海: ['上海市'],
  浙江: ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市', '金华市', '衢州市', '舟山市', '台州市', '丽水市'],
  江苏: ['南京市', '苏州市', '无锡市', '常州市', '南通市', '扬州市', '徐州市', '镇江市', '泰州市', '盐城市', '连云港市', '淮安市', '宿迁市'],
  四川: ['成都市', '绵阳市', '德阳市', '南充市', '宜宾市', '自贡市', '乐山市', '泸州市', '达州市', '内江市', '遂宁市', '攀枝花市', '眉山市', '广安市', '资阳市', '凉山州'],
  湖北: ['武汉市', '宜昌市', '襄阳市', '荆州市', '十堰市', '黄石市', '荆门市', '鄂州市', '孝感市', '黄冈市', '咸宁市', '随州市', '恩施州'],
  陕西: ['西安市', '咸阳市', '宝鸡市', '渭南市', '汉中市', '榆林市', '延安市', '安康市', '商洛市', '铜川市'],
  山东: ['济南市', '青岛市', '烟台市', '潍坊市', '临沂市', '淄博市', '济宁市', '泰安市', '威海市', '德州市', '聊城市', '滨州市', '菏泽市', '枣庄市', '日照市', '东营市'],
  河南: ['郑州市', '洛阳市', '南阳市', '许昌市', '周口市', '商丘市', '新乡市', '安阳市', '信阳市', '开封市', '平顶山市', '驻马店市', '焦作市', '漯河市', '濮阳市', '三门峡市', '鹤壁市', '许昌市'],
  福建: ['福州市', '厦门市', '泉州市', '漳州市', '莆田市', '龙岩市', '三明市', '南平市', '宁德市'],
  湖南: ['长沙市', '株洲市', '湘潭市', '衡阳市', '岳阳市', '常德市', '邵阳市', '益阳市', '娄底市', '郴州市', '永州市', '怀化市', '张家界市', '湘西州']
}
const PROVINCE_NAMES = Object.keys(PROVINCES)
const DEFAULT_PROVINCE = '广东'
const ALL_CITIES = PROVINCE_NAMES.flatMap((p) => PROVINCES[p])

type LocationStatus = 'loading' | 'success' | 'fail'

/**
 * P38 城市选择页 - 选择/切换当前城市，作为 AI 分析/验收规范/材料价格等本地化依据
 */
const CityPickerPage: React.FC = () => {
  const [keyword, setKeyword] = useState('')
  const [selectedProvince, setSelectedProvince] = useState(DEFAULT_PROVINCE)
  const [selectedCity, setSelectedCity] = useState('')
  const [locationStatus, setLocationStatus] = useState<LocationStatus>('loading')
  const [locationCityName, setLocationCityName] = useState<string>('')

  const filteredCities = useMemo(() => {
    const kw = keyword.trim().toLowerCase()
    if (!kw) return []
    return ALL_CITIES.filter((c) => c.toLowerCase().includes(kw) || c.replace(/市$/, '').toLowerCase().includes(kw))
  }, [keyword])

  const cityList = selectedProvince ? (PROVINCES[selectedProvince] || []) : []

  // 进入页面自动定位
  useEffect(() => {
    Taro.getLocation({
      type: 'wgs84',
      success: () => {
        setLocationStatus('success')
        // 无逆地理时用已选城市或占位
        const saved = Taro.getStorageSync('selected_city') as string
        setLocationCityName(saved || '当前城市')
      },
      fail: () => setLocationStatus('fail')
    })
  }, [])

  const handleConfirm = () => {
    const city = selectedCity || (filteredCities.length === 1 ? filteredCities[0] : '')
    if (!city) return
    Taro.setStorageSync('selected_city', city)
    const pages = Taro.getCurrentPages()
    if (pages.length > 1) {
      Taro.navigateBack()
    } else {
      safeSwitchTab(TAB_HOME, { defer: 100 })
    }
    Taro.showToast({
      title: `您已切换至${city}，后续AI分析将基于该城市的本地规范，历史报告不受影响`,
      icon: 'none',
      duration: 3000
    })
  }

  const hasSelection = !!selectedCity || (keyword.trim() && filteredCities.length === 1)

  return (
    <View className='city-picker-page'>
      {/* 顶部导航栏：左返回、中标题、右无 */}
      <View className='nav-bar'>
        <View className='nav-back' onClick={() => Taro.navigateBack()}>
          <Text className='nav-back-arrow'>←</Text>
        </View>
        <Text className='nav-title'>选择城市</Text>
        <View className='nav-right' />
      </View>

      <ScrollView scrollY className='city-picker-scroll' enhanced showScrollbar={false}>
        {/* 定位提示区 */}
        <View className='location-tip'>
          {locationStatus === 'loading' && (
            <>
              <Text className='location-icon'>📍</Text>
              <Text className='location-text loading'>定位中...</Text>
            </>
          )}
          {locationStatus === 'success' && (
            <>
              <Text className='location-icon'>📍</Text>
              <Text className='location-text'>当前定位城市：</Text>
              <Text className='location-city'>{locationCityName}</Text>
            </>
          )}
          {locationStatus === 'fail' && (
            <>
              <Text className='location-icon'>⚠️</Text>
              <Text className='location-text fail'>定位失败，请手动选择城市</Text>
            </>
          )}
        </View>

        {/* 热门城市 */}
        <View className='hot-section'>
          <Text className='section-title'>热门城市</Text>
          <View className='hot-underline' />
          <View className='hot-tags'>
            {HOT_CITIES.map((c) => (
              <View
                key={c.value}
                className={`hot-tag ${selectedCity === c.value ? 'active' : ''}`}
                onClick={() => setSelectedCity(c.value)}
              >
                <Text>{c.label}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* 城市搜索 */}
        <View className='search-section'>
          <View className='search-wrap'>
            <Text className='search-icon'>🔍</Text>
            <Input
              className='search-input'
              placeholder='输入城市名或拼音搜索'
              placeholderClass='search-placeholder'
              value={keyword}
              onInput={(e) => setKeyword(e.detail?.value || '')}
            />
          </View>
          {keyword.trim() && (
            <View className='search-result-wrap'>
              {filteredCities.length === 0 ? (
                <Text className='search-no-result'>未找到相关城市</Text>
              ) : (
                <View className='search-result-list'>
                  {filteredCities.map((c) => (
                    <View
                      key={c}
                      className={`search-result-item ${selectedCity === c ? 'active' : ''}`}
                      onClick={() => setSelectedCity(c)}
                    >
                      <Text>{c}</Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          )}
        </View>

        {/* 省份-城市选择区 */}
        {!keyword.trim() && (
          <View className='pick-section'>
            <View className='pick-row'>
              <ScrollView scrollY className='province-list' enhanced showScrollbar={false}>
                {PROVINCE_NAMES.map((p) => (
                  <View
                    key={p}
                    className={`province-item ${selectedProvince === p ? 'active' : ''}`}
                    onClick={() => { setSelectedProvince(p); setSelectedCity('') }}
                  >
                    <Text>{p}</Text>
                  </View>
                ))}
              </ScrollView>
              <ScrollView scrollY className='city-list' enhanced showScrollbar={false}>
                {cityList.map((c) => (
                  <View
                    key={c}
                    className={`city-item ${selectedCity === c ? 'active' : ''}`}
                    onClick={() => setSelectedCity(c)}
                  >
                    <Text>{c}</Text>
                  </View>
                ))}
              </ScrollView>
            </View>
          </View>
        )}
      </ScrollView>

      {/* 底部确认按钮：未选中置灰、选中高亮 */}
      <View className='footer'>
        <View
          className={`confirm-btn ${hasSelection ? 'active' : ''}`}
          onClick={hasSelection ? handleConfirm : undefined}
        >
          <Text className='btn-text'>确认选择</Text>
        </View>
      </View>
    </View>
  )
}

export default CityPickerPage
