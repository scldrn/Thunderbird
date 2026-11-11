import Foundation
import AVFoundation
import CoreVideo
import CoreGraphics
import ImageIO
let args=CommandLine.arguments
let folder=URL(fileURLWithPath:args[1]);let output=URL(fileURLWithPath:args[2]);let fps:Int32=15
let names=try FileManager.default.contentsOfDirectory(at:folder,includingPropertiesForKeys:nil).filter{$0.pathExtension=="png"}.sorted{$0.lastPathComponent<$1.lastPathComponent}
if FileManager.default.fileExists(atPath:output.path){try FileManager.default.removeItem(at:output)}
let writer=try AVAssetWriter(outputURL:output,fileType:.mp4)
let input=AVAssetWriterInput(mediaType:.video,outputSettings:[AVVideoCodecKey:AVVideoCodecType.h264,AVVideoWidthKey:1024,AVVideoHeightKey:640,AVVideoCompressionPropertiesKey:[AVVideoAverageBitRateKey:2500000]])
let adaptor=AVAssetWriterInputPixelBufferAdaptor(assetWriterInput:input,sourcePixelBufferAttributes:[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32ARGB,kCVPixelBufferWidthKey as String:1024,kCVPixelBufferHeightKey as String:640,kCVPixelBufferCGImageCompatibilityKey as String:true,kCVPixelBufferCGBitmapContextCompatibilityKey as String:true])
input.expectsMediaDataInRealTime=false;writer.add(input)
guard writer.startWriting() else{fatalError("writer start: \(String(describing:writer.error))")};writer.startSession(atSourceTime:.zero)
for (i,url) in names.enumerated(){
 while !input.isReadyForMoreMediaData {if writer.status == .failed{fatalError("\(String(describing:writer.error))")};Thread.sleep(forTimeInterval:0.002)}
 try autoreleasepool {
  guard let src=CGImageSourceCreateWithURL(url as CFURL,nil),let cg=CGImageSourceCreateImageAtIndex(src,0,nil) else{fatalError("PNG")}
  var buf:CVPixelBuffer?;let status=CVPixelBufferPoolCreatePixelBuffer(nil,adaptor.pixelBufferPool!,&buf)
  guard status==kCVReturnSuccess,let pixel=buf else{fatalError("pixel")}
  CVPixelBufferLockBaseAddress(pixel,[])
  let ctx=CGContext(data:CVPixelBufferGetBaseAddress(pixel),width:1024,height:640,bitsPerComponent:8,bytesPerRow:CVPixelBufferGetBytesPerRow(pixel),space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.noneSkipFirst.rawValue)!
  ctx.draw(cg,in:CGRect(x:0,y:0,width:1024,height:640));CVPixelBufferUnlockBaseAddress(pixel,[])
  guard adaptor.append(pixel,withPresentationTime:CMTime(value:Int64(i),timescale:fps)) else{fatalError("append \(String(describing:writer.error))")}
 }
}
input.markAsFinished();let sem=DispatchSemaphore(value:0);writer.finishWriting{sem.signal()};sem.wait()
guard writer.status == .completed else{fatalError("finish \(String(describing:writer.error))")}
print("VIDEO_OK \(names.count) frames")
