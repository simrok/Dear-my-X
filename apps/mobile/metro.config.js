// Metro config — Expo SDK 51 + pnpm 모노레포 최소 설정.
//
// 핵심:
//  1) Expo 의 getDefaultConfig 결과를 거의 그대로 사용
//  2) workspaceRoot 를 watchFolders 에 추가 → packages/shared 변경 감지
//  3) nodeModulesPaths 에 mobile + workspace 두 곳만 명시
//
// 의도적으로 하지 않는 것 (이전 에러의 원인):
//  - resolver.unstable_enableSymlinks 설정 X
//  - resolver.extraNodeModules 로 alias 박지 않음 (babel module-resolver 가 처리)
//  - resolver.unstable_enablePackageExports 설정 X
const { getDefaultConfig } = require('expo/metro-config');
const path = require('path');

const projectRoot = __dirname;
const workspaceRoot = path.resolve(projectRoot, '../..');

const config = getDefaultConfig(projectRoot);

config.watchFolders = [workspaceRoot];

config.resolver.nodeModulesPaths = [
  path.resolve(projectRoot, 'node_modules'),
  path.resolve(workspaceRoot, 'node_modules'),
];

module.exports = config;
