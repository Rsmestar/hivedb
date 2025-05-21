import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import * as THREE from 'three';

const HexLogo = ({ size = 200, animated = true }) => {
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
    
    // إنشاء السداسيات
    const hexagons = [];
    const hexRadius = 1;
    const hexHeight = 0.2;
    
    // إنشاء سداسي مركزي
    const centerHexGeometry = new THREE.CylinderGeometry(hexRadius, hexRadius, hexHeight, 6);
    const centerHexMaterial = new THREE.MeshPhongMaterial({
      color: 0x6A11CB,
      transparent: true,
      opacity: 0.9,
      shininess: 100
    });
    
    const centerHex = new THREE.Mesh(centerHexGeometry, centerHexMaterial);
    centerHex.rotation.x = Math.PI / 2;
    scene.add(centerHex);
    hexagons.push(centerHex);
    
    // إنشاء سداسيات محيطة
    const surroundingPositions = [
      { x: 1.73, y: 0 },
      { x: 0.865, y: 1.5 },
      { x: -0.865, y: 1.5 },
      { x: -1.73, y: 0 },
      { x: -0.865, y: -1.5 },
      { x: 0.865, y: -1.5 }
    ];
    
    surroundingPositions.forEach((pos, index) => {
      const hexGeometry = new THREE.CylinderGeometry(hexRadius * 0.7, hexRadius * 0.7, hexHeight, 6);
      const hexMaterial = new THREE.MeshPhongMaterial({
        color: 0x2575FC,
        transparent: true,
        opacity: 0.8,
        shininess: 100
      });
      
      const hex = new THREE.Mesh(hexGeometry, hexMaterial);
      hex.rotation.x = Math.PI / 2;
      hex.position.set(pos.x, pos.y, 0);
      scene.add(hex);
      hexagons.push(hex);
    });
    
    // إنشاء خطوط اتصال
    const lineMaterial = new THREE.LineBasicMaterial({ 
      color: 0xFFC107, 
      transparent: true,
      opacity: 0.6,
      linewidth: 2
    });
    
    surroundingPositions.forEach(pos => {
      const points = [];
      points.push(new THREE.Vector3(0, 0, 0));
      points.push(new THREE.Vector3(pos.x, pos.y, 0));
      
      const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(lineGeometry, lineMaterial);
      scene.add(line);
    });
    
    // تعيين موضع الكاميرا
    camera.position.z = 5;
    
    // وظيفة التحريك
    const animate = () => {
      if (!containerRef.current) return;
      
      if (animated) {
        centerHex.rotation.z += 0.01;
        
        hexagons.forEach((hex, index) => {
          if (index > 0) {
            hex.rotation.z -= 0.005;
            
            // تحريك السداسيات المحيطة للداخل والخارج
            const time = Date.now() * 0.001;
            const surroundingIndex = index - 1;
            const originalPos = surroundingPositions[surroundingIndex];
            const pulseAmount = Math.sin(time + surroundingIndex) * 0.1;
            
            hex.position.x = originalPos.x * (1 + pulseAmount);
            hex.position.y = originalPos.y * (1 + pulseAmount);
          }
        });
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
      ref={containerRef}
      sx={{
        width: size,
        height: size,
        margin: '0 auto',
        position: 'relative',
      }}
    />
  );
};

export default HexLogo;
