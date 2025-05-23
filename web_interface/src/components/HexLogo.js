import React, { useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';
import * as THREE from 'three';

const HexLogo = ({ size = 200, animated = true, showText = true }) => {
  const containerRef = useRef(null);
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    // إنشاء المشهد
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(size, size);
    renderer.setClearColor(0x000000, 0);
    
    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(renderer.domElement);
    
    // إضافة إضاءة
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 10, 10);
    scene.add(directionalLight);
    
    const pointLight = new THREE.PointLight(0x6A11CB, 1, 100);
    pointLight.position.set(0, 0, 10);
    scene.add(pointLight);
    
    // إنشاء السداسيات بتصميم أكثر أناقة وحداثة
    const hexagons = [];
    const hexRadius = 1;
    const hexHeight = 0.15; // أرق قليلاً للمظهر الحديث
    
    // إنشاء سداسي مركزي
    const centerHexGeometry = new THREE.CylinderGeometry(hexRadius, hexRadius, hexHeight, 6);
    const centerHexMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x3a86ff,
      transparent: true,
      opacity: 0.9,
      metalness: 0.5,
      roughness: 0.2,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1
    });
    
    const centerHex = new THREE.Mesh(centerHexGeometry, centerHexMaterial);
    centerHex.rotation.x = Math.PI / 2;
    scene.add(centerHex);
    hexagons.push(centerHex);
    
    // إنشاء طبقة ثانية للسداسي المركزي (تأثير متعدد الطبقات)
    const innerHexGeometry = new THREE.CylinderGeometry(hexRadius * 0.7, hexRadius * 0.7, hexHeight * 1.1, 6);
    const innerHexMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x4361ee,
      transparent: true,
      opacity: 0.9,
      metalness: 0.7,
      roughness: 0.1,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1
    });
    
    const innerHex = new THREE.Mesh(innerHexGeometry, innerHexMaterial);
    innerHex.rotation.x = Math.PI / 2;
    innerHex.position.z = 0.02;
    scene.add(innerHex);
    hexagons.push(innerHex);
    
    // إنشاء سداسيات محيطة بتباعد متناسق
    const surroundingPositions = [
      { x: 1.73, y: 0 },
      { x: 0.865, y: 1.5 },
      { x: -0.865, y: 1.5 },
      { x: -1.73, y: 0 },
      { x: -0.865, y: -1.5 },
      { x: 0.865, y: -1.5 }
    ];
    
    // ألوان متدرجة للسداسيات المحيطة
    const colors = [
      0x4cc9f0, // أزرق فاتح
      0x4895ef, // أزرق
      0x4361ee, // أزرق داكن
      0x3f37c9, // أزرق بنفسجي
      0x3a0ca3, // بنفسجي
      0x480ca8  // بنفسجي داكن
    ];
    
    surroundingPositions.forEach((pos, index) => {
      const hexGeometry = new THREE.CylinderGeometry(hexRadius * 0.6, hexRadius * 0.6, hexHeight, 6);
      const hexMaterial = new THREE.MeshPhysicalMaterial({
        color: colors[index],
        transparent: true,
        opacity: 0.85,
        metalness: 0.4,
        roughness: 0.3,
        clearcoat: 0.8,
        clearcoatRoughness: 0.2
      });
      
      const hex = new THREE.Mesh(hexGeometry, hexMaterial);
      hex.rotation.x = Math.PI / 2;
      hex.position.set(pos.x, pos.y, 0);
      scene.add(hex);
      hexagons.push(hex);
    });
    
    // إنشاء خطوط اتصال أكثر أناقة
    surroundingPositions.forEach((pos, index) => {
      // استخدام منحنيات بدلاً من خطوط مستقيمة للحصول على مظهر أكثر انسيابية
      const curve = new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(pos.x * 0.5, pos.y * 0.5, 0.2),
        new THREE.Vector3(pos.x, pos.y, 0)
      );
      
      const points = curve.getPoints(20);
      const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
      
      // استخدام لون متدرج يتناسب مع السداسي المتصل به
      const lineMaterial = new THREE.LineBasicMaterial({ 
        color: colors[index], 
        transparent: true,
        opacity: 0.5,
        linewidth: 1
      });
      
      const line = new THREE.Line(lineGeometry, lineMaterial);
      scene.add(line);
      
      // إضافة نقاط صغيرة على طول المنحنى لتأثير بصري أفضل
      const dotGeometry = new THREE.SphereGeometry(0.03, 8, 8);
      const dotMaterial = new THREE.MeshBasicMaterial({ 
        color: colors[index],
        transparent: true,
        opacity: 0.7
      });
      
      // إضافة 3 نقاط على طول المنحنى
      [0.25, 0.5, 0.75].forEach(t => {
        const pointOnCurve = curve.getPointAt(t);
        const dot = new THREE.Mesh(dotGeometry, dotMaterial);
        dot.position.copy(pointOnCurve);
        scene.add(dot);
      });
    });
    
    // تعيين موضع الكاميرا
    camera.position.z = 5;
    
    // وظيفة التحريك المحسنة
    const animate = () => {
      if (!containerRef.current) return;
      
      if (animated) {
        // دوران سلس للسداسي المركزي
        centerHex.rotation.z += 0.005;
        innerHex.rotation.z -= 0.008;
        
        // حركة أكثر تعقيدًا وجاذبية للسداسيات
        const time = Date.now() * 0.001;
        
        hexagons.forEach((hex, index) => {
          if (index > 1) { // تجاوز السداسيين المركزيين
            // دوران عكسي بسرعات مختلفة
            hex.rotation.z -= 0.003 + (index * 0.001);
            
            // تحريك السداسيات المحيطة بنمط موجي متناغم
            const surroundingIndex = index - 2;
            if (surroundingIndex < surroundingPositions.length) {
              const originalPos = surroundingPositions[surroundingIndex];
              // استخدام دالة جيب وجيب تمام لحركة أكثر تعقيدًا
              const pulseX = Math.sin(time * 0.8 + surroundingIndex) * 0.07;
              const pulseY = Math.cos(time * 0.7 + surroundingIndex) * 0.07;
              
              hex.position.x = originalPos.x * (1 + pulseX);
              hex.position.y = originalPos.y * (1 + pulseY);
              // إضافة حركة خفيفة على المحور Z
              hex.position.z = Math.sin(time * 0.5 + surroundingIndex) * 0.05;
            }
          }
        });
        
        // تحريك الكاميرا بشكل خفيف للحصول على تأثير ثلاثي الأبعاد أفضل
        camera.position.x = Math.sin(time * 0.3) * 0.2;
        camera.position.y = Math.cos(time * 0.2) * 0.2;
        camera.lookAt(0, 0, 0);
      }
      
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    
    animate();
    
    // تنظيف المشهد عند إزالة المكون
    const currentContainer = containerRef.current;
    return () => {
      if (currentContainer) {
        currentContainer.innerHTML = '';
      }
    };
  }, [size, animated]);
  
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto',
      }}
    >
      <Box
        ref={containerRef}
        sx={{
          width: size,
          height: size,
          position: 'relative',
        }}
      />
      {showText && (
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(90deg, #4cc9f0 0%, #3a0ca3 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '0.05em',
            mt: 2,
            fontFamily: '"Poppins", "Tajawal", sans-serif',
          }}
        >
          HiveDB
        </Typography>
      )}
    </Box>
  );
};

export default HexLogo;
