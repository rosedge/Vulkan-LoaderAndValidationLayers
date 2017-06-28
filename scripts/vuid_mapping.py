#!/usr/bin/python -i

import sys
import xml.etree.ElementTree as etree
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import json

#############################
# vuid_mapping.py script
#
# VUID Mapping Details
#  The Vulkan spec creation process automatically generates string-based unique IDs for each Valid Usage statement
#  For implicit VUs, the format is VUID-<func|struct>-[<param_name>]-<type>
#   func|struct is the name of the API function or structure that the VU is under
#   param_name is an optional entry with the name of the function or struct parameter
#   type is the type of implicit check, see table below for possible values
#
#  For explicit VUs, the format is VUID-<func|struct>-[<param_name>]-<uniqueid>
#   All fields are the same as implicit VUs except the last parameter is a globally unique integer ID instead of a string type
#
# The values below are used to map the strings into unique integers that are used for the unique enum values returned by debug callbacks
# Here's how the bits of the numerical unique ID map to the ID type and values
# 31:21 - 11 bits that map to unique value for the function/struct
# 20:1  - 20 bits that map to param-type combo for implicit VU and uniqueid for explicit VU
# 0     - 1 bit on for implicit VU or off for explicit VU
#
# For implicit VUs 20:1 is split into 20:9 for parameter and 8:1 for type
FUNC_STRUCT_SHIFT = 21
EXPLICIT_ID_SHIFT = 1
IMPLICIT_TYPE_SHIFT = 1
IMPLICIT_PARAM_SHIFT = 9
explicit_bit0 = 0x0 # All explicit IDs are even
implicit_bit0 = 0x1 # All implicit IDs are odd
# Implicit type values, shifted up by ID_SHIFT bits in final ID
implicit_type_map = {
'parameter'       : 0,
'requiredbitmask' : 1,
'zerobitmask'     : 2,
'parent'          : 3,
'commonparent'    : 4,
'sType'           : 5,
'pNext'           : 6,
'unique'          : 7,
'queuetype'       : 8,
'recording'       : 9,
'cmdpool'         : 10,
'renderpass'      : 11,
'bufferlevel'     : 12,
'arraylength'     : 13,
}
# Function/struct value mappings, shifted up FUNC_STRUCT_SHIFT bits in final ID
func_struct_id_map = {
'VkAcquireNextImageInfoKHX' : 0,
'VkAllocationCallbacks' : 1,
'VkAndroidSurfaceCreateInfoKHR' : 2,
'VkApplicationInfo' : 3,
'VkAttachmentDescription' : 4,
'VkAttachmentReference' : 5,
'VkBindBufferMemoryInfoKHX' : 6,
'VkBindImageMemoryInfoKHX' : 7,
'VkBindImageMemorySwapchainInfoKHX' : 8,
'VkBindSparseInfo' : 9,
'VkBufferCreateInfo' : 10,
'VkBufferImageCopy' : 11,
'VkBufferMemoryBarrier' : 12,
'VkBufferViewCreateInfo' : 13,
'VkClearAttachment' : 14,
'VkClearDepthStencilValue' : 15,
'VkClearValue' : 16,
'VkCmdProcessCommandsInfoNVX' : 17,
'VkCmdReserveSpaceForCommandsInfoNVX' : 18,
'VkCommandBufferAllocateInfo' : 19,
'VkCommandBufferBeginInfo' : 20,
'VkCommandBufferInheritanceInfo' : 21,
'VkCommandPoolCreateInfo' : 22,
'VkComponentMapping' : 23,
'VkComputePipelineCreateInfo' : 24,
'VkCopyDescriptorSet' : 25,
'VkD3D12FenceSubmitInfoKHX' : 26,
'VkDebugMarkerMarkerInfoEXT' : 27,
'VkDebugMarkerObjectNameInfoEXT' : 28,
'VkDebugMarkerObjectTagInfoEXT' : 29,
'VkDebugReportCallbackCreateInfoEXT' : 30,
'VkDedicatedAllocationBufferCreateInfoNV' : 31,
'VkDedicatedAllocationImageCreateInfoNV' : 32,
'VkDedicatedAllocationMemoryAllocateInfoNV' : 33,
'VkDescriptorBufferInfo' : 34,
'VkDescriptorImageInfo' : 35,
'VkDescriptorPoolCreateInfo' : 36,
'VkDescriptorPoolSize' : 37,
'VkDescriptorSetAllocateInfo' : 38,
'VkDescriptorSetLayoutBinding' : 39,
'VkDescriptorSetLayoutCreateInfo' : 40,
'VkDescriptorUpdateTemplateCreateInfoKHR' : 41,
'VkDescriptorUpdateTemplateEntryKHR' : 42,
'VkDeviceCreateInfo' : 43,
'VkDeviceEventInfoEXT' : 44,
'VkDeviceGeneratedCommandsFeaturesNVX' : 45,
'VkDeviceGeneratedCommandsLimitsNVX' : 46,
'VkDeviceGroupBindSparseInfoKHX' : 47,
'VkDeviceGroupCommandBufferBeginInfoKHX' : 48,
'VkDeviceGroupDeviceCreateInfoKHX' : 49,
'VkDeviceGroupPresentInfoKHX' : 50,
'VkDeviceGroupRenderPassBeginInfoKHX' : 51,
'VkDeviceGroupSubmitInfoKHX' : 52,
'VkDeviceGroupSwapchainCreateInfoKHX' : 53,
'VkDeviceQueueCreateInfo' : 54,
'VkDispatchIndirectCommand' : 55,
'VkDisplayEventInfoEXT' : 56,
'VkDisplayModeCreateInfoKHR' : 57,
'VkDisplayPowerInfoEXT' : 58,
'VkDisplayPresentInfoKHR' : 59,
'VkDisplaySurfaceCreateInfoKHR' : 60,
'VkDrawIndexedIndirectCommand' : 61,
'VkDrawIndirectCommand' : 62,
'VkEventCreateInfo' : 63,
'VkExportMemoryAllocateInfoKHX' : 64,
'VkExportMemoryAllocateInfoNV' : 65,
'VkExportMemoryWin32HandleInfoKHX' : 66,
'VkExportMemoryWin32HandleInfoNV' : 67,
'VkExportSemaphoreCreateInfoKHX' : 68,
'VkExportSemaphoreWin32HandleInfoKHX' : 69,
'VkExternalMemoryBufferCreateInfoKHX' : 70,
'VkExternalMemoryImageCreateInfoKHX' : 71,
'VkExternalMemoryImageCreateInfoNV' : 72,
'VkFenceCreateInfo' : 73,
'VkFramebufferCreateInfo' : 74,
'VkGraphicsPipelineCreateInfo' : 75,
'VkIOSSurfaceCreateInfoMVK' : 76,
'VkImageBlit' : 77,
'VkImageCopy' : 78,
'VkImageCreateInfo' : 79,
'VkImageMemoryBarrier' : 80,
'VkImageResolve' : 81,
'VkImageSubresource' : 82,
'VkImageSubresourceLayers' : 83,
'VkImageSubresourceRange' : 84,
'VkImageSwapchainCreateInfoKHX' : 85,
'VkImageViewCreateInfo' : 86,
'VkImportMemoryFdInfoKHX' : 87,
'VkImportMemoryWin32HandleInfoKHX' : 88,
'VkImportMemoryWin32HandleInfoNV' : 89,
'VkImportSemaphoreFdInfoKHX' : 90,
'VkImportSemaphoreWin32HandleInfoKHX' : 91,
'VkIndirectCommandsLayoutCreateInfoNVX' : 92,
'VkIndirectCommandsLayoutTokenNVX' : 93,
'VkIndirectCommandsTokenNVX' : 94,
'VkInstanceCreateInfo' : 95,
'VkMacOSSurfaceCreateInfoMVK' : 96,
'VkMappedMemoryRange' : 97,
'VkMemoryAllocateFlagsInfoKHX' : 98,
'VkMemoryAllocateInfo' : 99,
'VkMemoryBarrier' : 100,
'VkMirSurfaceCreateInfoKHR' : 101,
'VkObjectTableCreateInfoNVX' : 102,
'VkObjectTableDescriptorSetEntryNVX' : 103,
'VkObjectTableEntryNVX' : 104,
'VkObjectTableIndexBufferEntryNVX' : 105,
'VkObjectTablePipelineEntryNVX' : 106,
'VkObjectTablePushConstantEntryNVX' : 107,
'VkObjectTableVertexBufferEntryNVX' : 108,
'VkPhysicalDeviceDiscardRectanglePropertiesEXT' : 109,
'VkPhysicalDeviceExternalBufferInfoKHX' : 110,
'VkPhysicalDeviceExternalImageFormatInfoKHX' : 111,
'VkPhysicalDeviceExternalSemaphoreInfoKHX' : 112,
'VkPhysicalDeviceFeatures' : 113,
'VkPhysicalDeviceFeatures2KHR' : 114,
'VkPhysicalDeviceImageFormatInfo2KHR' : 115,
'VkPhysicalDeviceMultiviewFeaturesKHX' : 116,
'VkPhysicalDevicePushDescriptorPropertiesKHR' : 117,
'VkPhysicalDeviceSparseImageFormatInfo2KHR' : 118,
'VkPhysicalDeviceSurfaceInfo2KHR' : 119,
'VkPipelineCacheCreateInfo' : 120,
'VkPipelineColorBlendAttachmentState' : 121,
'VkPipelineColorBlendStateCreateInfo' : 122,
'VkPipelineDepthStencilStateCreateInfo' : 123,
'VkPipelineDiscardRectangleStateCreateInfoEXT' : 124,
'VkPipelineDynamicStateCreateInfo' : 125,
'VkPipelineInputAssemblyStateCreateInfo' : 126,
'VkPipelineLayoutCreateInfo' : 127,
'VkPipelineMultisampleStateCreateInfo' : 128,
'VkPipelineRasterizationStateCreateInfo' : 129,
'VkPipelineRasterizationStateRasterizationOrderAMD' : 130,
'VkPipelineShaderStageCreateInfo' : 131,
'VkPipelineTessellationStateCreateInfo' : 132,
'VkPipelineVertexInputStateCreateInfo' : 133,
'VkPipelineViewportStateCreateInfo' : 134,
'VkPipelineViewportSwizzleStateCreateInfoNV' : 135,
'VkPipelineViewportWScalingStateCreateInfoNV' : 136,
'VkPresentInfoKHR' : 137,
'VkPresentRegionKHR' : 138,
'VkPresentRegionsKHR' : 139,
'VkPresentTimesInfoGOOGLE' : 140,
'VkPushConstantRange' : 141,
'VkQueryPoolCreateInfo' : 142,
'VkRectLayerKHR' : 143,
'VkRenderPassBeginInfo' : 144,
'VkRenderPassCreateInfo' : 145,
'VkRenderPassMultiviewCreateInfoKHX' : 146,
'VkSamplerCreateInfo' : 147,
'VkSemaphoreCreateInfo' : 148,
'VkShaderModuleCreateInfo' : 149,
'VkSparseBufferMemoryBindInfo' : 150,
'VkSparseImageMemoryBind' : 151,
'VkSparseImageMemoryBindInfo' : 152,
'VkSparseImageOpaqueMemoryBindInfo' : 153,
'VkSparseMemoryBind' : 154,
'VkSpecializationInfo' : 155,
'VkSpecializationMapEntry' : 156,
'VkStencilOpState' : 157,
'VkSubmitInfo' : 158,
'VkSubpassDependency' : 159,
'VkSubpassDescription' : 160,
'VkSurfaceCapabilities2EXT' : 161,
'VkSwapchainCounterCreateInfoEXT' : 162,
'VkSwapchainCreateInfoKHR' : 163,
'VkValidationFlagsEXT' : 164,
'VkVertexInputAttributeDescription' : 165,
'VkVertexInputBindingDescription' : 166,
'VkViSurfaceCreateInfoNN' : 167,
'VkViewport' : 168,
'VkViewportSwizzleNV' : 169,
'VkWaylandSurfaceCreateInfoKHR' : 170,
'VkWin32KeyedMutexAcquireReleaseInfoKHX' : 171,
'VkWin32KeyedMutexAcquireReleaseInfoNV' : 172,
'VkWin32SurfaceCreateInfoKHR' : 173,
'VkWriteDescriptorSet' : 174,
'VkXcbSurfaceCreateInfoKHR' : 175,
'VkXlibSurfaceCreateInfoKHR' : 176,
'vkAcquireNextImage2KHX' : 177,
'vkAcquireNextImageKHR' : 178,
'vkAcquireXlibDisplayEXT' : 179,
'vkAllocateCommandBuffers' : 180,
'vkAllocateDescriptorSets' : 181,
'vkAllocateMemory' : 182,
'vkBeginCommandBuffer' : 183,
'vkBindBufferMemory' : 184,
'vkBindBufferMemory2KHX' : 185,
'vkBindImageMemory' : 186,
'vkBindImageMemory2KHX' : 187,
'vkCmdBeginQuery' : 188,
'vkCmdBeginRenderPass' : 189,
'vkCmdBindDescriptorSets' : 190,
'vkCmdBindIndexBuffer' : 191,
'vkCmdBindPipeline' : 192,
'vkCmdBindVertexBuffers' : 193,
'vkCmdBlitImage' : 194,
'vkCmdClearAttachments' : 195,
'vkCmdClearColorImage' : 196,
'vkCmdClearDepthStencilImage' : 197,
'vkCmdCopyBuffer' : 198,
'vkCmdCopyBufferToImage' : 199,
'vkCmdCopyImage' : 200,
'vkCmdCopyImageToBuffer' : 201,
'vkCmdCopyQueryPoolResults' : 202,
'vkCmdDebugMarkerBeginEXT' : 203,
'vkCmdDebugMarkerEndEXT' : 204,
'vkCmdDebugMarkerInsertEXT' : 205,
'vkCmdDispatch' : 206,
'vkCmdDispatchBaseKHX' : 207,
'vkCmdDispatchIndirect' : 208,
'vkCmdDraw' : 209,
'vkCmdDrawIndexed' : 210,
'vkCmdDrawIndexedIndirect' : 211,
'vkCmdDrawIndexedIndirectCountAMD' : 212,
'vkCmdDrawIndirect' : 213,
'vkCmdDrawIndirectCountAMD' : 214,
'vkCmdEndQuery' : 215,
'vkCmdEndRenderPass' : 216,
'vkCmdExecuteCommands' : 217,
'vkCmdFillBuffer' : 218,
'vkCmdNextSubpass' : 219,
'vkCmdPipelineBarrier' : 220,
'vkCmdProcessCommandsNVX' : 221,
'vkCmdPushConstants' : 222,
'vkCmdPushDescriptorSetKHR' : 223,
'vkCmdPushDescriptorSetWithTemplateKHR' : 224,
'vkCmdReserveSpaceForCommandsNVX' : 225,
'vkCmdResetEvent' : 226,
'vkCmdResetQueryPool' : 227,
'vkCmdResolveImage' : 228,
'vkCmdSetBlendConstants' : 229,
'vkCmdSetDepthBias' : 230,
'vkCmdSetDepthBounds' : 231,
'vkCmdSetDeviceMaskKHX' : 232,
'vkCmdSetDiscardRectangleEXT' : 233,
'vkCmdSetEvent' : 234,
'vkCmdSetLineWidth' : 235,
'vkCmdSetScissor' : 236,
'vkCmdSetStencilCompareMask' : 237,
'vkCmdSetStencilReference' : 238,
'vkCmdSetStencilWriteMask' : 239,
'vkCmdSetViewport' : 240,
'vkCmdSetViewportWScalingNV' : 241,
'vkCmdUpdateBuffer' : 242,
'vkCmdWaitEvents' : 243,
'vkCmdWriteTimestamp' : 244,
'vkCreateAndroidSurfaceKHR' : 245,
'vkCreateBuffer' : 246,
'vkCreateBufferView' : 247,
'vkCreateCommandPool' : 248,
'vkCreateComputePipelines' : 249,
'vkCreateDebugReportCallbackEXT' : 250,
'vkCreateDescriptorPool' : 251,
'vkCreateDescriptorSetLayout' : 252,
'vkCreateDescriptorUpdateTemplateKHR' : 253,
'vkCreateDevice' : 254,
'vkCreateDisplayModeKHR' : 255,
'vkCreateDisplayPlaneSurfaceKHR' : 256,
'vkCreateEvent' : 257,
'vkCreateFence' : 258,
'vkCreateFramebuffer' : 259,
'vkCreateGraphicsPipelines' : 260,
'vkCreateIOSSurfaceMVK' : 261,
'vkCreateImage' : 262,
'vkCreateImageView' : 263,
'vkCreateIndirectCommandsLayoutNVX' : 264,
'vkCreateInstance' : 265,
'vkCreateMacOSSurfaceMVK' : 266,
'vkCreateMirSurfaceKHR' : 267,
'vkCreateObjectTableNVX' : 268,
'vkCreatePipelineCache' : 269,
'vkCreatePipelineLayout' : 270,
'vkCreateQueryPool' : 271,
'vkCreateRenderPass' : 272,
'vkCreateSampler' : 273,
'vkCreateSemaphore' : 274,
'vkCreateShaderModule' : 275,
'vkCreateSharedSwapchainsKHR' : 276,
'vkCreateSwapchainKHR' : 277,
'vkCreateViSurfaceNN' : 278,
'vkCreateWaylandSurfaceKHR' : 279,
'vkCreateWin32SurfaceKHR' : 280,
'vkCreateXcbSurfaceKHR' : 281,
'vkCreateXlibSurfaceKHR' : 282,
'vkDebugMarkerSetObjectNameEXT' : 283,
'vkDebugMarkerSetObjectTagEXT' : 284,
'vkDebugReportMessageEXT' : 285,
'vkDestroyBuffer' : 286,
'vkDestroyBufferView' : 287,
'vkDestroyCommandPool' : 288,
'vkDestroyDebugReportCallbackEXT' : 289,
'vkDestroyDescriptorPool' : 290,
'vkDestroyDescriptorSetLayout' : 291,
'vkDestroyDescriptorUpdateTemplateKHR' : 292,
'vkDestroyDevice' : 293,
'vkDestroyEvent' : 294,
'vkDestroyFence' : 295,
'vkDestroyFramebuffer' : 296,
'vkDestroyImage' : 297,
'vkDestroyImageView' : 298,
'vkDestroyIndirectCommandsLayoutNVX' : 299,
'vkDestroyInstance' : 300,
'vkDestroyObjectTableNVX' : 301,
'vkDestroyPipeline' : 302,
'vkDestroyPipelineCache' : 303,
'vkDestroyPipelineLayout' : 304,
'vkDestroyQueryPool' : 305,
'vkDestroyRenderPass' : 306,
'vkDestroySampler' : 307,
'vkDestroySemaphore' : 308,
'vkDestroyShaderModule' : 309,
'vkDestroySurfaceKHR' : 310,
'vkDestroySwapchainKHR' : 311,
'vkDeviceWaitIdle' : 312,
'vkDisplayPowerControlEXT' : 313,
'vkEndCommandBuffer' : 314,
'vkEnumerateDeviceExtensionProperties' : 315,
'vkEnumerateDeviceLayerProperties' : 316,
'vkEnumerateInstanceExtensionProperties' : 317,
'vkEnumerateInstanceLayerProperties' : 318,
'vkEnumeratePhysicalDeviceGroupsKHX' : 319,
'vkEnumeratePhysicalDevices' : 320,
'vkFlushMappedMemoryRanges' : 321,
'vkFreeCommandBuffers' : 322,
'vkFreeDescriptorSets' : 323,
'vkFreeMemory' : 324,
'vkGetBufferMemoryRequirements' : 325,
'vkGetDeviceGroupPeerMemoryFeaturesKHX' : 326,
'vkGetDeviceGroupPresentCapabilitiesKHX' : 327,
'vkGetDeviceGroupSurfacePresentModesKHX' : 328,
'vkGetDeviceMemoryCommitment' : 329,
'vkGetDeviceProcAddr' : 330,
'vkGetDeviceQueue' : 331,
'vkGetDisplayModePropertiesKHR' : 332,
'vkGetDisplayPlaneCapabilitiesKHR' : 333,
'vkGetDisplayPlaneSupportedDisplaysKHR' : 334,
'vkGetEventStatus' : 335,
'vkGetFenceStatus' : 336,
'vkGetImageMemoryRequirements' : 337,
'vkGetImageSparseMemoryRequirements' : 338,
'vkGetImageSubresourceLayout' : 339,
'vkGetInstanceProcAddr' : 340,
'vkGetMemoryFdKHX' : 341,
'vkGetMemoryFdPropertiesKHX' : 342,
'vkGetMemoryWin32HandleKHX' : 343,
'vkGetMemoryWin32HandleNV' : 344,
'vkGetMemoryWin32HandlePropertiesKHX' : 345,
'vkGetPastPresentationTimingGOOGLE' : 346,
'vkGetPhysicalDeviceDisplayPlanePropertiesKHR' : 347,
'vkGetPhysicalDeviceDisplayPropertiesKHR' : 348,
'vkGetPhysicalDeviceExternalBufferPropertiesKHX' : 349,
'vkGetPhysicalDeviceExternalImageFormatPropertiesNV' : 350,
'vkGetPhysicalDeviceExternalSemaphorePropertiesKHX' : 351,
'vkGetPhysicalDeviceFeatures' : 352,
'vkGetPhysicalDeviceFeatures2KHR' : 353,
'vkGetPhysicalDeviceFormatProperties' : 354,
'vkGetPhysicalDeviceFormatProperties2KHR' : 355,
'vkGetPhysicalDeviceGeneratedCommandsPropertiesNVX' : 356,
'vkGetPhysicalDeviceImageFormatProperties' : 357,
'vkGetPhysicalDeviceImageFormatProperties2KHR' : 358,
'vkGetPhysicalDeviceMemoryProperties' : 359,
'vkGetPhysicalDeviceMemoryProperties2KHR' : 360,
'vkGetPhysicalDeviceMirPresentationSupportKHR' : 361,
'vkGetPhysicalDevicePresentRectanglesKHX' : 362,
'vkGetPhysicalDeviceProperties' : 363,
'vkGetPhysicalDeviceProperties2KHR' : 364,
'vkGetPhysicalDeviceQueueFamilyProperties' : 365,
'vkGetPhysicalDeviceQueueFamilyProperties2KHR' : 366,
'vkGetPhysicalDeviceSparseImageFormatProperties' : 367,
'vkGetPhysicalDeviceSparseImageFormatProperties2KHR' : 368,
'vkGetPhysicalDeviceSurfaceCapabilities2EXT' : 369,
'vkGetPhysicalDeviceSurfaceCapabilities2KHR' : 370,
'vkGetPhysicalDeviceSurfaceCapabilitiesKHR' : 371,
'vkGetPhysicalDeviceSurfaceFormats2KHR' : 372,
'vkGetPhysicalDeviceSurfaceFormatsKHR' : 373,
'vkGetPhysicalDeviceSurfacePresentModesKHR' : 374,
'vkGetPhysicalDeviceSurfaceSupportKHR' : 375,
'vkGetPhysicalDeviceWaylandPresentationSupportKHR' : 376,
'vkGetPhysicalDeviceWin32PresentationSupportKHR' : 377,
'vkGetPhysicalDeviceXcbPresentationSupportKHR' : 378,
'vkGetPhysicalDeviceXlibPresentationSupportKHR' : 379,
'vkGetPipelineCacheData' : 380,
'vkGetQueryPoolResults' : 381,
'vkGetRandROutputDisplayEXT' : 382,
'vkGetRefreshCycleDurationGOOGLE' : 383,
'vkGetRenderAreaGranularity' : 384,
'vkGetSemaphoreFdKHX' : 385,
'vkGetSemaphoreWin32HandleKHX' : 386,
'vkGetSwapchainCounterEXT' : 387,
'vkGetSwapchainImagesKHR' : 388,
'vkGetSwapchainStatusKHR' : 389,
'vkImportSemaphoreFdKHX' : 390,
'vkImportSemaphoreWin32HandleKHX' : 391,
'vkInvalidateMappedMemoryRanges' : 392,
'vkMapMemory' : 393,
'vkMergePipelineCaches' : 394,
'vkQueueBindSparse' : 395,
'vkQueuePresentKHR' : 396,
'vkQueueSubmit' : 397,
'vkQueueWaitIdle' : 398,
'vkRegisterDeviceEventEXT' : 399,
'vkRegisterDisplayEventEXT' : 400,
'vkRegisterObjectsNVX' : 401,
'vkReleaseDisplayEXT' : 402,
'vkResetCommandBuffer' : 403,
'vkResetCommandPool' : 404,
'vkResetDescriptorPool' : 405,
'vkResetEvent' : 406,
'vkResetFences' : 407,
'vkSetEvent' : 408,
'vkSetHdrMetadataEXT' : 409,
'vkTrimCommandPoolKHR' : 410,
'vkUnmapMemory' : 411,
'vkUnregisterObjectsNVX' : 412,
'vkUpdateDescriptorSetWithTemplateKHR' : 413,
'vkUpdateDescriptorSets' : 414,
'vkWaitForFences' : 415,
'VkPhysicalDeviceProperties2KHR' : 416,
'VkFormatProperties2KHR' : 417,
'VkImageFormatProperties2KHR' : 418,
'VkPhysicalDeviceMemoryProperties2KHR' : 419,
'VkSurfaceCapabilities2KHR' : 420,
'VkDeviceGroupPresentCapabilitiesKHX' : 421,
'VkExternalBufferPropertiesKHX' : 422,
'VkMemoryWin32HandlePropertiesKHX' : 423,
'VkMemoryFdPropertiesKHX' : 424,
'VkExternalSemaphorePropertiesKHX' : 425,
'VkQueueFamilyProperties2KHR' : 426,
'VkSparseImageFormatProperties2KHR' : 427,
'VkSurfaceFormat2KHR' : 428,
'VkTextureLODGatherFormatPropertiesAMD' : 429,
'VkPhysicalDeviceMultiviewPropertiesKHX' : 430,
'VkPhysicalDeviceGroupPropertiesKHX' : 431,
'VkExternalImageFormatPropertiesKHX' : 432,
'VkPhysicalDeviceIDPropertiesKHX' : 433,
'VkPhysicalDeviceMultiviewPerViewAttributesPropertiesNVX' : 434,
'VkHdrMetadataEXT' : 435,
'VkExternalMemoryPropertiesKHX' : 436,
'VkFormatProperties' : 437,
'VkImageFormatProperties' : 438,
'VkPhysicalDeviceLimits' : 439,
'VkQueueFamilyProperties' : 440,
'VkMemoryType' : 441,
'VkMemoryHeap' : 442,
'VkSparseImageFormatProperties' : 443,
'VkSurfaceCapabilitiesKHR' : 444,
'VkDisplayPropertiesKHR' : 445,
'VkDisplayPlaneCapabilitiesKHR' : 446,
'VkSharedPresentSurfaceCapabilitiesKHR' : 447,
'VkExternalImageFormatPropertiesNV' : 448,
'VkPhysicalDeviceBlendOperationAdvancedFeaturesEXT' : 449,
'VkPhysicalDeviceBlendOperationAdvancedPropertiesEXT' : 450,
'VkPhysicalDeviceSamplerFilterMinmaxPropertiesEXT' : 451,
'VkPipelineColorBlendAdvancedStateCreateInfoEXT' : 452,
'VkPipelineCoverageModulationStateCreateInfoNV' : 453,
'VkPipelineCoverageToColorStateCreateInfoNV' : 454,
'VkSamplerReductionModeCreateInfoEXT' : 455,
### ADD New func/struct mappings above this line
}
# Mapping of params to unique IDs
implicit_param_map = {
'a' : 0,
'addressModeU' : 1,
'addressModeV' : 2,
'addressModeW' : 3,
'alphaBlendOp' : 4,
'alphaMode' : 5,
'aspectMask' : 6,
'attachmentCount' : 7,
'b' : 8,
'back' : 9,
'bindCount' : 10,
'bindInfoCount' : 11,
'bindingCount' : 12,
'buffer' : 13,
'bufferView' : 14,
'callback' : 15,
'colorBlendOp' : 16,
'colorWriteMask' : 17,
'commandBuffer' : 18,
'commandBufferCount' : 19,
'commandPool' : 20,
'compareOp' : 21,
'components' : 22,
'compositeAlpha' : 23,
'connection' : 24,
'contents' : 25,
'countBuffer' : 26,
'counter' : 27,
'createInfoCount' : 28,
'cullMode' : 29,
'dataSize' : 30,
'dependencyFlags' : 31,
'depthCompareOp' : 32,
'depthFailOp' : 33,
'descriptorCount' : 34,
'descriptorPool' : 35,
'descriptorSet' : 36,
'descriptorSetCount' : 37,
'descriptorSetLayout' : 38,
'descriptorType' : 39,
'descriptorUpdateEntryCount' : 40,
'descriptorUpdateTemplate' : 41,
'descriptorWriteCount' : 42,
'device' : 43,
'deviceEvent' : 44,
'disabledValidationCheckCount' : 45,
'discardRectangleCount' : 46,
'discardRectangleMode' : 47,
'display' : 48,
'displayEvent' : 49,
'displayMode' : 50,
'dpy' : 51,
'dstAccessMask' : 52,
'dstAlphaBlendFactor' : 53,
'dstBuffer' : 54,
'dstCache' : 55,
'dstColorBlendFactor' : 56,
'dstImage' : 57,
'dstImageLayout' : 58,
'dstSet' : 59,
'dstStageMask' : 60,
'dstSubresource' : 61,
'dynamicStateCount' : 62,
'event' : 63,
'eventCount' : 64,
'externalHandleType' : 65,
'faceMask' : 66,
'failOp' : 67,
'fence' : 68,
'fenceCount' : 69,
'filter' : 70,
'finalLayout' : 71,
'flags' : 72,
'format' : 73,
'framebuffer' : 74,
'front' : 75,
'frontFace' : 76,
'g' : 77,
'handleType' : 78,
'handleTypes' : 79,
'image' : 80,
'imageColorSpace' : 81,
'imageFormat' : 82,
'imageLayout' : 83,
'imageSharingMode' : 84,
'imageSubresource' : 85,
'imageType' : 86,
'imageUsage' : 87,
'imageView' : 88,
'indexType' : 89,
'indirectCommandsLayout' : 90,
'indirectCommandsTokenCount' : 91,
'initialLayout' : 92,
'inputRate' : 93,
'instance' : 94,
'layout' : 95,
'level' : 96,
'loadOp' : 97,
'magFilter' : 98,
'memory' : 99,
'memoryRangeCount' : 100,
'minFilter' : 101,
'mipmapMode' : 102,
'mode' : 103,
'modes' : 104,
'module' : 105,
'newLayout' : 106,
'objectCount' : 107,
'objectTable' : 108,
'objectType' : 109,
'oldLayout' : 110,
'oldSwapchain' : 111,
'pAcquireInfo' : 112,
'pAcquireKeys' : 113,
'pAcquireSyncs' : 114,
'pAcquireTimeoutMilliseconds' : 115,
'pAcquireTimeouts' : 116,
'pAllocateInfo' : 117,
'pAllocator' : 118,
'pApplicationInfo' : 119,
'pApplicationName' : 120,
'pAttachments' : 121,
'pAttributes' : 122,
'pBeginInfo' : 123,
'pBindInfo' : 124,
'pBindInfos' : 125,
'pBindings' : 126,
'pBinds' : 127,
'pBuffer' : 128,
'pBufferBinds' : 129,
'pBufferMemoryBarriers' : 130,
'pBuffers' : 131,
'pCallback' : 132,
'pCapabilities' : 133,
'pCode' : 134,
'pColor' : 135,
'pColorAttachments' : 136,
'pCommandBufferDeviceMasks' : 137,
'pCommandBuffers' : 138,
'pCommandPool' : 139,
'pCommittedMemoryInBytes' : 140,
'pCorrelationMasks' : 141,
'pCounterValue' : 142,
'pCreateInfo' : 143,
'pCreateInfos' : 144,
'pData' : 145,
'pDataSize' : 146,
'pDependencies' : 147,
'pDepthStencil' : 148,
'pDepthStencilAttachment' : 149,
'pDescriptorCopies' : 150,
'pDescriptorPool' : 151,
'pDescriptorSets' : 152,
'pDescriptorUpdateEntries' : 153,
'pDescriptorUpdateTemplate' : 154,
'pDescriptorWrites' : 155,
'pDevice' : 156,
'pDeviceEventInfo' : 157,
'pDeviceGroupPresentCapabilities' : 158,
'pDeviceIndices' : 159,
'pDeviceMasks' : 160,
'pDeviceRenderAreas' : 161,
'pDisabledValidationChecks' : 162,
'pDiscardRectangles' : 163,
'pDisplay' : 164,
'pDisplayCount' : 165,
'pDisplayEventInfo' : 166,
'pDisplayPowerInfo' : 167,
'pDisplayTimingProperties' : 168,
'pDisplays' : 169,
'pDynamicOffsets' : 170,
'pDynamicState' : 171,
'pDynamicStates' : 172,
'pEnabledFeatures' : 173,
'pEngineName' : 174,
'pEvent' : 175,
'pEvents' : 176,
'pExternalBufferInfo' : 177,
'pExternalBufferProperties' : 178,
'pExternalImageFormatProperties' : 179,
'pExternalSemaphoreInfo' : 180,
'pExternalSemaphoreProperties' : 181,
'pFd' : 182,
'pFeatures' : 183,
'pFence' : 184,
'pFences' : 185,
'pFormatInfo' : 186,
'pFormatProperties' : 187,
'pFramebuffer' : 188,
'pGranularity' : 189,
'pHandle' : 190,
'pImage' : 191,
'pImageBinds' : 192,
'pImageFormatInfo' : 193,
'pImageFormatProperties' : 194,
'pImageIndex' : 195,
'pImageIndices' : 196,
'pImageMemoryBarriers' : 197,
'pImageOpaqueBinds' : 198,
'pImportSemaphoreFdInfo' : 199,
'pImportSemaphoreWin32HandleInfo' : 200,
'pIndirectCommandsLayout' : 201,
'pIndirectCommandsTokens' : 202,
'pInitialData' : 203,
'pInputAssemblyState' : 204,
'pInputAttachments' : 205,
'pInstance' : 206,
'pLayerName' : 207,
'pLayerPrefix' : 208,
'pLayout' : 209,
'pLimits' : 210,
'pMarkerInfo' : 211,
'pMarkerName' : 212,
'pMemory' : 213,
'pMemoryBarriers' : 214,
'pMemoryFdProperties' : 215,
'pMemoryProperties' : 216,
'pMemoryRanges' : 217,
'pMemoryRequirements' : 218,
'pMemoryWin32HandleProperties' : 219,
'pMessage' : 220,
'pMetadata' : 221,
'pMode' : 222,
'pModes' : 223,
'pName' : 224,
'pNameInfo' : 225,
'pNext' : 226,
'pObjectEntryCounts' : 227,
'pObjectEntryTypes' : 228,
'pObjectEntryUsageFlags' : 229,
'pObjectIndices' : 230,
'pObjectName' : 231,
'pObjectTable' : 232,
'pOffsets' : 233,
'pPeerMemoryFeatures' : 234,
'pPhysicalDeviceCount' : 235,
'pPhysicalDeviceGroupCount' : 236,
'pPhysicalDeviceGroupProperties' : 237,
'pPhysicalDevices' : 238,
'pPipelineCache' : 239,
'pPipelineLayout' : 240,
'pPipelines' : 241,
'pPoolSizes' : 242,
'pPresentInfo' : 243,
'pPresentModeCount' : 244,
'pPresentModes' : 245,
'pPresentationTimingCount' : 246,
'pPresentationTimings' : 247,
'pPreserveAttachments' : 248,
'pProcessCommandsInfo' : 249,
'pProperties' : 250,
'pPropertyCount' : 251,
'pPushConstantRanges' : 252,
'pQueryPool' : 253,
'pQueue' : 254,
'pQueueCreateInfos' : 255,
'pQueueFamilyProperties' : 256,
'pQueueFamilyPropertyCount' : 257,
'pQueuePriorities' : 258,
'pRanges' : 259,
'pRasterizationState' : 260,
'pRectCount' : 261,
'pRectangles' : 262,
'pRects' : 263,
'pRegions' : 264,
'pReleaseKeys' : 265,
'pReleaseSyncs' : 266,
'pRenderPass' : 267,
'pRenderPassBegin' : 268,
'pReserveSpaceInfo' : 269,
'pResolveAttachments' : 270,
'pResults' : 271,
'pSFRRects' : 272,
'pSampleMask' : 273,
'pSampler' : 274,
'pScissors' : 275,
'pSemaphore' : 276,
'pSetLayout' : 277,
'pSetLayouts' : 278,
'pShaderModule' : 279,
'pSignalSemaphoreDeviceIndices' : 280,
'pSignalSemaphoreValues' : 281,
'pSignalSemaphores' : 282,
'pSparseMemoryRequirementCount' : 283,
'pSparseMemoryRequirements' : 284,
'pSpecializationInfo' : 285,
'pSrcCaches' : 286,
'pStages' : 287,
'pSubmits' : 288,
'pSubpasses' : 289,
'pSubresource' : 290,
'pSupported' : 291,
'pSurface' : 292,
'pSurfaceCapabilities' : 293,
'pSurfaceFormatCount' : 294,
'pSurfaceFormats' : 295,
'pSurfaceInfo' : 296,
'pSwapchain' : 297,
'pSwapchainImageCount' : 298,
'pSwapchainImages' : 299,
'pSwapchains' : 300,
'pTag' : 301,
'pTagInfo' : 302,
'pTimes' : 303,
'pTokens' : 304,
'pValues' : 305,
'pVertexAttributeDescriptions' : 306,
'pVertexBindingDescriptions' : 307,
'pVertexInputState' : 308,
'pView' : 309,
'pViewMasks' : 310,
'pViewOffsets' : 311,
'pWaitDstStageMask' : 312,
'pWaitSemaphoreDeviceIndices' : 313,
'pWaitSemaphoreValues' : 314,
'pWaitSemaphores' : 315,
'passOp' : 316,
'physicalDevice' : 317,
'pipeline' : 318,
'pipelineBindPoint' : 319,
'pipelineCache' : 320,
'pipelineLayout' : 321,
'pipelineStage' : 322,
'polygonMode' : 323,
'poolSizeCount' : 324,
'powerState' : 325,
'ppData' : 326,
'ppEnabledExtensionNames' : 327,
'ppEnabledLayerNames' : 328,
'ppObjectTableEntries' : 329,
'preTransform' : 330,
'presentMode' : 331,
'queryPool' : 332,
'queryType' : 333,
'queue' : 334,
'queueCount' : 335,
'queueCreateInfoCount' : 336,
'r' : 337,
'rangeCount' : 338,
'rasterizationOrder' : 339,
'rasterizationSamples' : 340,
'rectCount' : 341,
'regionCount' : 342,
'renderPass' : 343,
'sType' : 344,
'sampler' : 345,
'samples' : 346,
'scissorCount' : 347,
'semaphore' : 348,
'sequencesCountBuffer' : 349,
'sequencesIndexBuffer' : 350,
'shaderModule' : 351,
'sharingMode' : 352,
'size' : 353,
'srcAccessMask' : 354,
'srcAlphaBlendFactor' : 355,
'srcBuffer' : 356,
'srcCacheCount' : 357,
'srcColorBlendFactor' : 358,
'srcImage' : 359,
'srcImageLayout' : 360,
'srcSet' : 361,
'srcStageMask' : 362,
'srcSubresource' : 363,
'stage' : 364,
'stageCount' : 365,
'stageFlags' : 366,
'stageMask' : 367,
'stencilLoadOp' : 368,
'stencilStoreOp' : 369,
'storeOp' : 370,
'subpassCount' : 371,
'subresource' : 372,
'subresourceRange' : 373,
'surface' : 374,
'surfaceCounters' : 375,
'swapchain' : 376,
'swapchainCount' : 377,
'tagSize' : 378,
'targetCommandBuffer' : 379,
'templateType' : 380,
'tiling' : 381,
'tokenCount' : 382,
'tokenType' : 383,
'topology' : 384,
'transform' : 385,
'type' : 386,
'usage' : 387,
'viewType' : 388,
'viewportCount' : 389,
'w' : 390,
'window' : 391,
'x' : 392,
'y' : 393,
'z' : 394,
'externalMemoryFeatures' : 395,
'compatibleHandleTypes' : 396,
'exportFromImportedHandleTypes' : 397,
'linearTilingFeatures' : 398,
'optimalTilingFeatures' : 399,
'bufferFeatures' : 400,
'sampleCounts' : 401,
'framebufferColorSampleCounts' : 402,
'framebufferDepthSampleCounts' : 403,
'framebufferStencilSampleCounts' : 404,
'framebufferNoAttachmentsSampleCounts' : 405,
'sampledImageColorSampleCounts' : 406,
'sampledImageIntegerSampleCounts' : 407,
'sampledImageDepthSampleCounts' : 408,
'sampledImageStencilSampleCounts' : 409,
'storageImageSampleCounts' : 410,
'queueFlags' : 411,
'propertyFlags' : 412,
'supportedTransforms' : 413,
'currentTransform' : 414,
'supportedCompositeAlpha' : 415,
'supportedUsageFlags' : 416,
'supportedAlpha' : 417,
'sharedPresentSupportedUsageFlags' : 418,
'externalSemaphoreFeatures' : 419,
'supportedSurfaceCounters' : 420,
'blendOverlap' : 421,
'coverageModulationMode' : 422,
'coverageModulationTableCount' : 423,
'reductionMode' : 424,
### ADD New implicit param mappings above this line
}

uniqueid_set = set() # store uniqueid to make sure we don't have duplicates

# Convert a string VUID into numerical value
#  See "VUID Mapping Details" comment above for more info
def convertVUID(vuid_string):
    """Convert a string-based VUID into a numberical value"""
    #func_struct_update = False
    #imp_param_update = False
    if vuid_string in ['', None]:
        return -1
    vuid_parts = vuid_string.split('-')
    if vuid_parts[1] not in func_struct_id_map:
        print ("ERROR: Missing func/struct map value for '%s'!" % (vuid_parts[1]))
        print (" TODO: Need to add mapping for this to end of func_struct_id_map")
        print ("   replace '### ADD New func/struct mappings above this line' line with \"'%s' : %d,\"" % (vuid_parts[1], len(func_struct_id_map)))
        func_struct_id_map[vuid_parts[1]] = len(func_struct_id_map)
        #func_struct_update = True
        sys.exit()
    uniqueid = func_struct_id_map[vuid_parts[1]] << FUNC_STRUCT_SHIFT
    if vuid_parts[-1].isdigit(): # explit VUID has int on the end
        explicit_id = int(vuid_parts[-1])
        # For explicit case, id is explicit_base + func/struct mapping + unique id
        uniqueid = uniqueid + (explicit_id << EXPLICIT_ID_SHIFT) + explicit_bit0
    else: # implicit case
        if vuid_parts[-1] not in implicit_type_map:
            print("ERROR: Missing mapping for implicit type '%s'!\nTODO: Please add new mapping." % (vuid_parts[-1]))
            sys.exit()
        else:
            param_id = 0 # Default when no param is available
            if vuid_parts[-2] != vuid_parts[1]: # we have a parameter
                if vuid_parts[-2] in implicit_param_map:
                    param_id = implicit_param_map[vuid_parts[-2]]
                else:
                    print ("ERROR: Missing param '%s' from implicit_param_map\n TODO: Please add new mapping." % (vuid_parts[-2]))
                    print ("   replace '### ADD New implicit param mappings above this line' line with \"'%s' : %d,\"" % (vuid_parts[-2], len(implicit_param_map)))
                    implicit_param_map[vuid_parts[-2]] = len(implicit_param_map)
                    #imp_param_update = True
                    sys.exit()
                uniqueid = uniqueid + (param_id << IMPLICIT_PARAM_SHIFT) + (implicit_type_map[vuid_parts[-1]] << IMPLICIT_TYPE_SHIFT) + implicit_bit0
            else: # No parameter so that field is 0
                uniqueid = uniqueid + (implicit_type_map[vuid_parts[-1]] << IMPLICIT_TYPE_SHIFT) + implicit_bit0
#    if uniqueid in uniqueid_set:
#        print ("ERROR: Uniqueid %d for string id %s is a duplicate!" % (uniqueid, vuid_string))
#        print (" TODO: Figure out what caused the dupe and fix it")
        #sys.exit()
    # print ("Storing uniqueid %d for unique string %s" % (uniqueid, vuid_string))
    uniqueid_set.add(uniqueid)
#    if func_struct_update:
#        print ("func_struct_id_map updated, here's new structure")
#        print ("func_struct_id_map = {")
#        fs_id = 0
#        for fs in sorted(func_struct_id_map):
#            print ("'%s' : %d," % (fs, fs_id))
#            fs_id = fs_id + 1
#        print ("### ADD New func/struct mappings above this line")
#        print ("}")
#    if imp_param_update:
#        print ("implicit_param_map updated, here's new structure")
#        print ("implicit_param_map = {")
#        ip_id = 0
#        for ip in sorted(implicit_param_map):
#            print ("'%s' : %d," % (ip, ip_id))
#            ip_id = ip_id + 1
#        print ("### ADD New implicit param mappings above this line")
#        print ("}")

    return uniqueid
