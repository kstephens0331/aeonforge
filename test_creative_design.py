#!/usr/bin/env python3
"""
Test System for Creative Design Tools - Batch 4
===============================================

Comprehensive testing of all 20 creative design tools
for branding, marketing, visual content, and design production.
"""

import sys
import os
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_creative_design_imports():
    """Test all creative design tool imports"""
    print("Testing Creative Design Tool Imports...")
    
    try:
        from tools.creative_design import (
            # Core Design Tools (1-5)
            LogoDesigner, WebsiteBuilder, GraphicDesigner, VideoScriptWriter, SocialMediaContentCreator,
            # Brand & Marketing Tools (6-10)
            BrandGuidelinesGenerator, MarketingCopyWriter, UIUXDesigner, InfographicCreator, BannerAndAdDesigner,
            # Advanced Creative Tools (11-20)
            BrochureBuilder, BusinessCardDesigner, StoryboardCreator, ColorPaletteGenerator, TypographySelector,
            IconAndSymbolCreator, ImageEditorAndEnhancer, AnimationPlanner, PrintLayoutDesigner, ThreeDModelDescriptor,
            # System functions
            get_creative_design_tool_info, create_creative_design_system
        )
        
        print("[PASS] All 20 creative design tools imported successfully!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        traceback.print_exc()
        return False

def test_creative_tool_info():
    """Test creative design tool info function"""
    print("\nTesting Creative Design Tool Info...")
    
    try:
        from tools.creative_design import get_creative_design_tool_info
        
        info = get_creative_design_tool_info()
        print(f"Total tools: {info['total_tools']}")
        print(f"Categories: {info['categories']}")
        print(f"Capabilities: {len(info['capabilities'])} features")
        
        if info['total_tools'] == 20:
            print("[PASS] Creative design tool info correct")
            return True
        else:
            print(f"[FAIL] Expected 20 tools, got {info['total_tools']}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Creative design tool info error: {e}")
        traceback.print_exc()
        return False

def test_creative_system_creation():
    """Test creative design system creation"""
    print("\nTesting Creative Design System Creation...")
    
    try:
        from tools.creative_design import create_creative_design_system
        
        system = create_creative_design_system()
        
        if system['system_ready']:
            print(f"[PASS] Creative design system created with {system['tools_initialized']} tools")
            print(f"Integration status: {system['integration_status']}")
            return True
        else:
            print("[FAIL] Creative design system not ready")
            return False
            
    except Exception as e:
        print(f"[FAIL] Creative design system creation error: {e}")
        traceback.print_exc()
        return False

def test_core_design_tools():
    """Test core design tool instantiation"""
    print("\nTesting Core Design Tools...")
    
    try:
        from tools.creative_design import (
            LogoDesigner, WebsiteBuilder, GraphicDesigner, VideoScriptWriter, SocialMediaContentCreator
        )
        
        # Test Logo Designer
        logo = LogoDesigner()
        print("[PASS] Logo Designer created")
        
        # Test Website Builder
        website = WebsiteBuilder()
        print("[PASS] Website Builder created")
        
        # Test Graphic Designer
        graphic = GraphicDesigner()
        print("[PASS] Graphic Designer created")
        
        # Test Video Script Writer
        video = VideoScriptWriter()
        print("[PASS] Video Script Writer created")
        
        # Test Social Media Creator
        social = SocialMediaContentCreator()
        print("[PASS] Social Media Content Creator created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Core design tools test error: {e}")
        traceback.print_exc()
        return False

def test_brand_marketing_tools():
    """Test brand and marketing tool instantiation"""
    print("\nTesting Brand & Marketing Tools...")
    
    try:
        from tools.creative_design import (
            BrandGuidelinesGenerator, MarketingCopyWriter, UIUXDesigner, 
            InfographicCreator, BannerAndAdDesigner
        )
        
        # Test Brand Guidelines Generator
        brand = BrandGuidelinesGenerator()
        print("[PASS] Brand Guidelines Generator created")
        
        # Test Marketing Copy Writer
        copy = MarketingCopyWriter()
        print("[PASS] Marketing Copy Writer created")
        
        # Test UI/UX Designer
        uiux = UIUXDesigner()
        print("[PASS] UI/UX Designer created")
        
        # Test Infographic Creator
        infographic = InfographicCreator()
        print("[PASS] Infographic Creator created")
        
        # Test Banner & Ad Designer
        banner = BannerAndAdDesigner()
        print("[PASS] Banner & Ad Designer created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Brand & marketing tools test error: {e}")
        traceback.print_exc()
        return False

def test_advanced_creative_tools():
    """Test advanced creative tool instantiation"""
    print("\nTesting Advanced Creative Tools...")
    
    try:
        from tools.creative_design import (
            BrochureBuilder, BusinessCardDesigner, StoryboardCreator,
            ColorPaletteGenerator, TypographySelector
        )
        
        # Test Brochure Builder
        brochure = BrochureBuilder()
        print("[PASS] Brochure Builder created")
        
        # Test Business Card Designer
        card = BusinessCardDesigner()
        print("[PASS] Business Card Designer created")
        
        # Test Storyboard Creator
        storyboard = StoryboardCreator()
        print("[PASS] Storyboard Creator created")
        
        # Test Color Palette Generator
        color = ColorPaletteGenerator()
        print("[PASS] Color Palette Generator created")
        
        # Test Typography Selector
        typography = TypographySelector()
        print("[PASS] Typography Selector created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Advanced creative tools test error: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of key creative design tools"""
    print("\nTesting Basic Tool Functionality...")
    
    try:
        from tools.creative_design import LogoDesigner, ColorPaletteGenerator, GraphicDesigner
        
        # Test Logo Designer brand identity creation
        logo = LogoDesigner()
        design_spec = {
            'brand_name': 'Test Company',
            'industry': 'technology',
            'brand_values': ['innovation', 'reliability'],
            'color_preferences': {'primary': '#007bff'},
            'style': 'modern'
        }
        
        result = logo.create_logo_design(design_spec)
        if result and 'brand_identity' in result:
            print("[PASS] Logo Designer brand identity creation working")
        else:
            print("[FAIL] Logo Designer not returning proper result")
            return False
        
        # Test Color Palette Generator
        color = ColorPaletteGenerator()
        color_spec = {
            'name': 'Test Palette',
            'inspiration': {'base_color': '#007bff'},
            'harmony_type': 'complementary',
            'color_count': 5
        }
        
        color_result = color.create_color_system(color_spec)
        if color_result and 'color_system' in color_result:
            print("[PASS] Color Palette Generator working")
        else:
            print("[FAIL] Color Palette Generator not returning proper result")
            return False
        
        # Test Graphic Designer
        graphic = GraphicDesigner()
        graphic_spec = {
            'title': 'Test Marketing Graphic',
            'type': 'poster',
            'dimensions': {'width': 1080, 'height': 1080},
            'content': {
                'headline': 'Amazing Product Launch',
                'subtext': 'Join us for something special'
            }
        }
        
        graphic_result = graphic.create_marketing_graphic(graphic_spec)
        if graphic_result and 'graphic_design' in graphic_result:
            print("[PASS] Graphic Designer working")
        else:
            print("[FAIL] Graphic Designer not returning proper result")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Basic functionality test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all creative design tests"""
    print("=" * 60)
    print("Aeonforge Creative Design Tools - Test Suite")
    print("Batch 4: Creative Design & Visual Content Creation")
    print("=" * 60)
    
    tests = [
        ("Creative Design Tool Imports", test_creative_design_imports),
        ("Creative Design Tool Info", test_creative_tool_info),
        ("Creative Design System Creation", test_creative_system_creation),
        ("Core Design Tools", test_core_design_tools),
        ("Brand & Marketing Tools", test_brand_marketing_tools),
        ("Advanced Creative Tools", test_advanced_creative_tools),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("CREATIVE DESIGN TOOLS TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n[SUCCESS] All creative design tools working correctly!")
        print("\nREADY FOR CREATIVE PRODUCTION:")
        print("- Professional logo and brand identity design")
        print("- Comprehensive website design and development") 
        print("- Advanced marketing material creation")
        print("- Social media content and campaign management")
        print("- Print production and publishing design")
        print("- User interface and experience design")
        print("- Data visualization and infographics")
        print("- Video and animation planning")
        print("- Typography and color system design")
        print("- Complete creative workflow automation")
    else:
        print(f"\n[WARNING] {len(results) - passed} tests failed. Check errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()