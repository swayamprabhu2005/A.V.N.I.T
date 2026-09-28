import * as PIXI from 'pixi.js'

export function usePixiOverlay() {
  let app = null
  let graphicsLayer = null
  let textLayer = null

  /**
   * Initializes the PixiJS WebGL application attached to the specified canvas element.
   */
  const initPixi = (canvasElement, width = 640, height = 360) => {
    if (app) {
      destroyPixi()
    }

    try {
      app = new PIXI.Application({
        view: canvasElement,
        width: width,
        height: height,
        backgroundAlpha: 0,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true
      })

      graphicsLayer = new PIXI.Graphics()
      textLayer = new PIXI.Container()

      app.stage.addChild(graphicsLayer)
      app.stage.addChild(textLayer)
    } catch (e) {
      console.warn('[AVNIT PixiJS] WebGL context initialization fallback:', e)
    }
  }

  /**
   * Updates HUD reticles and bounding overlays from the latest telemetry frame.
   * STRICT COLOR RULE: ZERO SHADES OF BLUE.
   */
  const updateOverlay = (telemetryList = [], videoWidth = 640, videoHeight = 360) => {
    if (!app || !graphicsLayer || !textLayer) return

    graphicsLayer.clear()
    textLayer.removeChildren()

    if (!telemetryList || telemetryList.length === 0) return

    const canvasWidth = app.screen.width
    const canvasHeight = app.screen.height

    const scaleX = canvasWidth / (videoWidth || 640)
    const scaleY = canvasHeight / (videoHeight || 360)

    telemetryList.forEach((item) => {
      const bbox = item.bbox || [0, 0, 0, 0]
      const x1 = bbox[0] * scaleX
      const y1 = bbox[1] * scaleY
      const x2 = bbox[2] * scaleX
      const y2 = bbox[3] * scaleY
      const w = Math.max(10, x2 - x1)
      const h = Math.max(10, y2 - y1)

      const riskScore = item.risk_result ? item.risk_result.risk_score : 10
      const isHighRisk = riskScore >= 60 || (item.risk_result && item.risk_result.risk_level === 'RED')
      const isWarning = riskScore >= 30 && riskScore < 60

      // Color scheme (Zero Blue): Emerald for Pass, Amber for Warning, Rose for Alert
      const primaryColor = isHighRisk ? 0xf43f5e : (isWarning ? 0xf59e0b : 0x10b981)
      const cornerLength = Math.min(18, w * 0.25, h * 0.25)
      const lineWidth = 2.5

      // 1. Tactical Corner Brackets
      graphicsLayer.lineStyle(lineWidth, primaryColor, 0.95)

      // Top-Left corner
      graphicsLayer.moveTo(x1, y1 + cornerLength)
      graphicsLayer.lineTo(x1, y1)
      graphicsLayer.lineTo(x1 + cornerLength, y1)

      // Top-Right corner
      graphicsLayer.moveTo(x2 - cornerLength, y1)
      graphicsLayer.lineTo(x2, y1)
      graphicsLayer.lineTo(x2, y1 + cornerLength)

      // Bottom-Left corner
      graphicsLayer.moveTo(x1, y2 - cornerLength)
      graphicsLayer.lineTo(x1, y2)
      graphicsLayer.lineTo(x1 + cornerLength, y2)

      // Bottom-Right corner
      graphicsLayer.moveTo(x2 - cornerLength, y2)
      graphicsLayer.lineTo(x2, y2)
      graphicsLayer.lineTo(x2, y2 - cornerLength)

      // 2. Subtle translucent inner fill
      graphicsLayer.lineStyle(1, primaryColor, 0.25)
      graphicsLayer.beginFill(primaryColor, 0.06)
      graphicsLayer.drawRect(x1, y1, w, h)
      graphicsLayer.endFill()

      // 3. Monospace HUD Plate Tag Card above box
      const plateText = (item.plate_number || 'SCANNING...').toUpperCase()
      const confPercent = Math.round((item.ocr_confidence || 0.95) * 100)
      const labelStr = `TRK #${item.track_id} | ${plateText} (${confPercent}%)`

      const tagHeight = 20
      const tagWidth = Math.max(120, labelStr.length * 7.5 + 14)
      const tagY = Math.max(2, y1 - tagHeight - 4)

      // Tag background (Dark Charcoal Onyx - ZERO BLUE)
      graphicsLayer.lineStyle(1, primaryColor, 0.8)
      graphicsLayer.beginFill(0x18181b, 0.92)
      graphicsLayer.drawRoundedRect(x1, tagY, tagWidth, tagHeight, 4)
      graphicsLayer.endFill()

      // Small Status Dot
      graphicsLayer.lineStyle(0)
      graphicsLayer.beginFill(primaryColor, 1.0)
      graphicsLayer.drawCircle(x1 + 8, tagY + tagHeight / 2, 3)
      graphicsLayer.endFill()

      // Tag Text
      const textStyle = new PIXI.TextStyle({
        fontFamily: 'JetBrains Mono, Courier, monospace',
        fontSize: 10,
        fontWeight: 'bold',
        fill: 0xffffff,
        letterSpacing: 0.5
      })

      const pixiText = new PIXI.Text(labelStr, textStyle)
      pixiText.x = x1 + 16
      pixiText.y = tagY + 3.5
      textLayer.addChild(pixiText)
    })
  }

  const resizePixi = (width, height) => {
    if (app && app.renderer) {
      app.renderer.resize(width, height)
    }
  }

  const destroyPixi = () => {
    if (app) {
      try {
        app.destroy(false, { children: true, texture: true, baseTexture: true })
      } catch (e) {
        console.warn('[AVNIT PixiJS] Cleanup note:', e)
      }
      app = null
      graphicsLayer = null
      textLayer = null
    }
  }

  return {
    initPixi,
    updateOverlay,
    resizePixi,
    destroyPixi
  }
}
