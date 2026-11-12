package com.wx.convertor

import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.RippleDrawable
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.text.InputType
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.File
import kotlin.concurrent.thread

class MainActivity : ComponentActivity() {

    private companion object {
        val BG = Color.parseColor("#0E1014")
        val CARD = Color.parseColor("#171A21")
        val FIELD = Color.parseColor("#1F232C")
        val STROKE = Color.parseColor("#2C323E")
        val ACCENT = Color.parseColor("#7C3AED")
        val ACCENT2 = Color.parseColor("#06B6D4")
        val TEXT = Color.parseColor("#F2F4F8")
        val MUTED = Color.parseColor("#8B93A3")
    }

    private var inputUri: Uri? = null
    private var inputName: String = ""
    private var resultZip: File? = null

    private lateinit var pickBox: LinearLayout
    private lateinit var pickPlus: TextView
    private lateinit var pickLabel: TextView
    private lateinit var nameEdit: EditText
    private lateinit var convertBtn: Button
    private lateinit var saveBtn: Button
    private lateinit var progress: ProgressBar
    private lateinit var status: TextView

    private val pickLauncher =
        registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
            if (uri != null) {
                inputUri = uri
                inputName = displayName(uri)
                pickPlus.text = "✓"
                pickPlus.setTextColor(ACCENT2)
                pickLabel.text = inputName
                pickLabel.setTextColor(TEXT)
                nameEdit.setText(inputName.substringBeforeLast('.') + "_bg")
                setEnabledUi(convertBtn, true)
                saveBtn.visibility = View.GONE
                resultZip = null
                status.text = ""
            }
        }

    private val saveLauncher =
        registerForActivityResult(ActivityResultContracts.CreateDocument("application/zip")) { uri ->
            val zip = resultZip
            if (uri != null && zip != null) {
                try {
                    contentResolver.openOutputStream(uri)?.use { out ->
                        zip.inputStream().use { it.copyTo(out) }
                    }
                    status.text = "Salvo ✓"
                    Toast.makeText(this, "ZIP salvo!", Toast.LENGTH_SHORT).show()
                } catch (e: Exception) {
                    status.text = "Erro ao salvar: ${e.message}"
                }
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!Python.isStarted()) Python.start(AndroidPlatform(this))
        window.statusBarColor = BG
        window.navigationBarColor = BG
        buildUi()
    }

    // ------------------------------------------------------------------ UI
    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    private fun rounded(color: Int, radius: Int, stroke: Int? = null) = GradientDrawable().apply {
        setColor(color)
        cornerRadius = dp(radius).toFloat()
        if (stroke != null) setStroke(dp(1), stroke)
    }

    private fun ripple(bg: GradientDrawable) =
        RippleDrawable(ColorStateList.valueOf(Color.parseColor("#33FFFFFF")), bg, null)

    private fun setEnabledUi(b: View, enabled: Boolean) {
        b.isEnabled = enabled
        b.alpha = if (enabled) 1f else 0.4f
    }

    private fun lp(h: Int = ViewGroup.LayoutParams.WRAP_CONTENT, top: Int = 0) =
        LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, h).apply { topMargin = dp(top) }

    private fun buildUi() {
        val title = TextView(this).apply {
            text = "WxConvertor"
            textSize = 30f
            setTypeface(typeface, Typeface.BOLD)
            setTextColor(TEXT)
            gravity = Gravity.CENTER
            letterSpacing = 0.02f
        }

        // caixa de escolher arquivo
        pickPlus = TextView(this).apply {
            text = "+"
            textSize = 38f
            setTextColor(ACCENT)
            gravity = Gravity.CENTER
        }
        pickLabel = TextView(this).apply {
            text = "ZIP"
            textSize = 15f
            setTextColor(MUTED)
            gravity = Gravity.CENTER
            maxLines = 2
        }
        pickBox = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(dp(16), dp(20), dp(16), dp(20))
            background = ripple(rounded(FIELD, 16, STROKE))
            isClickable = true
            setOnClickListener { pickLauncher.launch(arrayOf("*/*")) }
            addView(pickPlus)
            addView(pickLabel)
        }

        nameEdit = EditText(this).apply {
            hint = "nome do zip"
            setHintTextColor(MUTED)
            setTextColor(TEXT)
            textSize = 16f
            inputType = InputType.TYPE_CLASS_TEXT
            setSingleLine()
            background = rounded(FIELD, 14, STROKE)
            setPadding(dp(16), dp(14), dp(16), dp(14))
        }

        convertBtn = Button(this).apply {
            text = "Converter"
            isAllCaps = false
            textSize = 17f
            setTypeface(typeface, Typeface.BOLD)
            setTextColor(Color.WHITE)
            stateListAnimator = null
            background = ripple(GradientDrawable(
                GradientDrawable.Orientation.LEFT_RIGHT, intArrayOf(ACCENT, ACCENT2)
            ).apply { cornerRadius = dp(16).toFloat() })
            setOnClickListener { startConversion() }
        }
        setEnabledUi(convertBtn, false)

        saveBtn = Button(this).apply {
            text = "Salvar ZIP"
            isAllCaps = false
            textSize = 16f
            setTextColor(TEXT)
            stateListAnimator = null
            background = ripple(rounded(FIELD, 16, STROKE))
            visibility = View.GONE
            setOnClickListener { saveLauncher.launch(outputName()) }
        }

        progress = ProgressBar(this).apply {
            isIndeterminate = true
            indeterminateTintList = ColorStateList.valueOf(ACCENT2)
            visibility = View.GONE
        }

        status = TextView(this).apply {
            textSize = 14f
            setTextColor(MUTED)
            gravity = Gravity.CENTER
        }

        val card = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(18), dp(18), dp(18))
            background = rounded(CARD, 24, STROKE)
            addView(pickBox, lp())
            addView(nameEdit, lp(top = 12))
            addView(convertBtn, lp(h = dp(54), top = 16))
            addView(saveBtn, lp(h = dp(50), top = 10))
        }

        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(22), dp(40), dp(22), dp(32))
            addView(title, lp())
            addView(card, lp(top = 32))
            addView(progress, lp(top = 24))
            addView(status, lp(top = 16))
        }

        val scroll = ScrollView(this).apply {
            setBackgroundColor(BG)
            isFillViewport = true
            addView(FrameLayout(context).apply { addView(column) })
        }
        setContentView(scroll)
    }

    // ------------------------------------------------------------ lógica
    private fun displayName(uri: Uri): String {
        contentResolver.query(uri, null, null, null, null)?.use { c ->
            val i = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (i >= 0 && c.moveToFirst()) return c.getString(i)
        }
        return "pack.zip"
    }

    private fun outputName(): String {
        var n = nameEdit.text.toString().trim().replace(Regex("[\\\\/:*?\"<>|]"), "_")
        if (n.isEmpty()) n = inputName.substringBeforeLast('.') + "_bg"
        if (!n.lowercase().endsWith(".zip")) n += ".zip"
        return n
    }

    private fun prepareReference(): File {
        val dir = File(filesDir, "bg_reference").apply { mkdirs() }
        for (name in assets.list("bg_reference").orEmpty()) {
            val dest = File(dir, name)
            if (!dest.exists()) {
                assets.open("bg_reference/$name").use { i -> dest.outputStream().use { o -> i.copyTo(o) } }
            }
        }
        return dir
    }

    private fun startConversion() {
        val uri = inputUri ?: return
        val outName = outputName()
        setEnabledUi(convertBtn, false)
        pickBox.isEnabled = false
        saveBtn.visibility = View.GONE
        progress.visibility = View.VISIBLE
        status.text = "Convertendo..."

        thread {
            var zipPath: String? = null
            try {
                val work = File(cacheDir, "work").apply { deleteRecursively(); mkdirs() }
                val ext = inputName.substringAfterLast('.', "zip")
                val inFile = File(work, "entrada.$ext")
                contentResolver.openInputStream(uri)!!.use { i -> inFile.outputStream().use { o -> i.copyTo(o) } }
                val outDir = File(work, "saida").apply { mkdirs() }
                val ref = prepareReference()

                val res = Python.getInstance().getModule("wx_app")
                    .callAttr("convert", inFile.absolutePath, outDir.absolutePath, outName, ref.absolutePath)
                    .asList()
                zipPath = res[0].toString()
                inFile.delete()
            } catch (e: Exception) {
                runOnUiThread { finishUi(null, "Erro: ${e.message}") }
                return@thread
            }
            runOnUiThread { finishUi(zipPath, "Pronto ✓") }
        }
    }

    private fun finishUi(zipPath: String?, message: String) {
        progress.visibility = View.GONE
        pickBox.isEnabled = true
        setEnabledUi(convertBtn, true)
        status.text = message
        if (zipPath != null) {
            resultZip = File(zipPath)
            saveBtn.visibility = View.VISIBLE
            saveLauncher.launch(outputName())
        }
    }
}
