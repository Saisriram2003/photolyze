import tifffile
import xml.etree.ElementTree as ET

def parse_xmp(xmp_bytes):
    """
    Parse the XMP XML data (from bytes) and extract a comprehensive set
    of editing parameters from the Camera Raw Settings (crs:) namespace.
    Returns a dictionary with the extracted parameters.
    """
    try:
        xmp_str = xmp_bytes.decode('utf-8', errors='replace')
        root = ET.fromstring(xmp_str)
    except ET.ParseError as e:
        print("Error parsing XMP metadata:", e)
        return {}

    # Define the XML namespaces
    ns = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'crs': 'http://ns.adobe.com/camera-raw-settings/1.0/'
    }

    # List of Camera Raw Settings keys to extract.
    # These include global adjustments, white balance, exposure, tonal and color settings,
    # as well as per-channel adjustments and other processing parameters.
    keys_to_extract = [
        'Version',
        'ProcessVersion',
        'WhiteBalance',
        'Temperature',       # Controls warmth/coolness
        'Tint',              # Green–magenta balance
        'Exposure',
        'Shadows',
        'Brightness',
        'Contrast',
        'Saturation',
        'Sharpness',
        'LuminanceSmoothing',
        'ColorNoiseReduction',
        'ChromaticAberrationR',
        'ChromaticAberrationB',
        'VignetteAmount',
        'ShadowTint',
        'RedHue',
        'RedSaturation',
        'GreenHue',
        'GreenSaturation',
        'BlueHue',
        'BlueSaturation',
        'FillLight',
        'Vibrance',
        'HighlightRecovery',
        'Clarity',
        'Defringe',
        'HueAdjustmentRed',
        'HueAdjustmentOrange',
        'HueAdjustmentYellow',
        'HueAdjustmentGreen',
        'HueAdjustmentAqua',
        'HueAdjustmentBlue',
        'HueAdjustmentPurple',
        'HueAdjustmentMagenta',
        'SaturationAdjustmentRed',
        'SaturationAdjustmentOrange',
        'SaturationAdjustmentYellow',
        'SaturationAdjustmentGreen',
        'SaturationAdjustmentAqua',
        'SaturationAdjustmentBlue',
        'SaturationAdjustmentPurple',
        'SaturationAdjustmentMagenta',
        'LuminanceAdjustmentRed',
        'LuminanceAdjustmentOrange',
        'LuminanceAdjustmentYellow',
        'LuminanceAdjustmentGreen',
        'LuminanceAdjustmentAqua',
        'LuminanceAdjustmentBlue',
        'LuminanceAdjustmentPurple',
        'LuminanceAdjustmentMagenta',
        'SplitToningShadowHue',
        'SplitToningShadowSaturation',
        'SplitToningHighlightHue',
        'SplitToningHighlightSaturation',
        'SplitToningBalance',
        'ParametricShadows',
        'ParametricDarks',
        'ParametricLights',
        'ParametricHighlights',
        'ParametricShadowSplit',
        'ParametricMidtoneSplit',
        'ParametricHighlightSplit',
        'SharpenRadius',
        'SharpenDetail',
        'SharpenEdgeMasking',
        'PostCropVignetteAmount',
        'GrainAmount',
        'LensProfileEnable',
        'LensManualDistortionAmount',
        'PerspectiveVertical',
        'PerspectiveHorizontal',
        'PerspectiveRotate',
        'PerspectiveScale',
        'ConvertToGrayscale',
        'ToneCurveName',
        'CameraProfile',
        'LensProfileSetup',
        'HasSettings',
        'HasCrop',
        'AlreadyApplied'
    ]

    editing_params = {}

    # Iterate through all rdf:Description elements and extract crs: keys.
    for desc in root.findall('.//rdf:Description', ns):
        for key in keys_to_extract:
            val = desc.findtext('crs:' + key, default=None, namespaces=ns)
            if val is not None:
                editing_params[key] = val

        # Special handling for ToneCurve, which is often a sequence.
        tone_curve_elem = desc.find('crs:ToneCurve', ns)
        if tone_curve_elem is not None:
            li_elements = tone_curve_elem.findall('.//rdf:li', ns)
            tone_curve_values = [li.text for li in li_elements if li.text is not None]
            if tone_curve_values:
                editing_params['ToneCurve'] = tone_curve_values

    return editing_params

def extract_editing_metadata(file_path):
    """
    Open the TIFF file using tifffile, extract the XMP metadata,
    and parse it to retrieve all relevant editing adjustments.
    """
    try:
        with tifffile.TiffFile(file_path) as tif:
            xmp_data = None
            # Look for the XMP tag among the TIFF tags (usually on the first page)
            for tag in tif.pages[0].tags.values():
                if tag.name == 'XMP':
                    xmp_data = tag.value
                    break

            if xmp_data is None:
                print("No XMP metadata found in the file.")
                return None

            # Parse the XMP data to extract editing parameters
            editing_params = parse_xmp(xmp_data)
            return editing_params

    except Exception as e:
        print(f"Error extracting editing metadata: {e}")
        return None

if __name__ == '__main__':
    file_path = 'images/a0001-jmac_DSC1459.tif'
    editing_metadata = extract_editing_metadata(file_path)

    if editing_metadata:
        print("Extracted Editing Metadata:")
        for key, value in editing_metadata.items():
            print(f"{key}: {value}")
    else:
        print("No editing metadata could be extracted.")
